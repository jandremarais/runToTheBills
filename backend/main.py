import asyncio
import os
import time
from dataclasses import dataclass
from typing import Optional

import motor.motor_asyncio
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from pydantic import BaseModel
from pymongo import ReturnDocument

load_dotenv()


@dataclass
class Strava:
    id: str = os.environ["strava_client_id"]
    secret: str = os.environ["strava_client_secret"]
    url: str = "https://www.strava.com"
    api: str = "/api/v3"


@dataclass
class Investec:
    url: str = "https://openapi.investec.com"


@dataclass
class Host:
    url: str = "http://localhost:8000"
    verify_token: str = os.environ["verify_token"]


app = FastAPI(title="Run to the Bills")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mongo_client = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017)
db = mongo_client.runtothebills


@app.get("/strava/auth/{user}", response_class=RedirectResponse)
def start_strava_auth(user: str):
    scope = "read,activity:read_all,profile:read_all"
    redirect_url = (
        f"{Host.url}/strava/exchange_token/{user}&approval_prompt=force&scope={scope}"
    )
    auth_url = f"{Strava.url}/oauth/authorize?client_id={Strava.id}&response_type=code&redirect_uri={redirect_url}"
    return auth_url


@app.get("/strava/exchange_token/{user}", response_class=RedirectResponse)
async def strava_exchange_token(user: str, scope: str, code: str, state: str):
    if scope != "read,activity:read_all,profile:read_all":
        raise HTTPException(status_code=400, detail="Invalid Scope")

    async with AsyncClient(base_url=Strava.url) as client:
        response = await client.post(
            "/oauth/token",
            data={
                "client_id": Strava.id,
                "client_secret": Strava.secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        data = response.json()

    data["user"] = user
    athlete = data.pop("athlete")
    athlete["user"] = user
    await db.stravaTokens.insert_one(data)
    await db.athletes.insert_one(athlete)

    return "http://localhost:3000"


@app.get("/user/{user}")
async def get_user(user: str):
    doc = await db.users.find_one({"user": user})
    # del doc["_id"]
    return doc


class InvestecCreds(BaseModel):
    id: str
    secret: str


@app.post("/investec/auth/{user}")
async def start_investec_auth(cred: InvestecCreds, user: str):
    await db.investecCreds.find_one_and_update(
        {"user": user},
        {"$set": {"user": user, "client_id": cred.id, "client_secret": cred.secret}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    await refresh_investec_token(user)
    await sync_accounts(user)


async def refresh_investec_token(user):
    creds = await db.investecCreds.find_one({"user": user})

    async with AsyncClient(
        base_url=Investec.url, auth=(creds["client_id"], creds["client_secret"])
    ) as client:
        response = await client.post(
            "/identity/v2/oauth2/token",
            data={
                "scope": "accounts",
                "grant_type": "client_credentials",
            },
        )
        data = response.json()
    data["expires_at"] = time.time() + data["expires_in"]
    data["user"] = user
    result = await db.investecTokens.find_one_and_update(
        {"user": user},
        {"$set": data},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return result


async def sync_accounts(user):
    tokens = await db.investecTokens.find_one({"user": user})

    if time.time() >= tokens["expires_at"]:
        tokens = await refresh_investec_token(user)

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    async with AsyncClient(base_url=Investec.url, headers=headers) as client:
        response = await client.get("/za/pb/v1/accounts")
        data = response.json()

    for account in data["data"]["accounts"]:
        account["user"] = user
        await db.accounts.insert_one(account)


@app.get("/accounts/{user}")
async def get_accounts(user: str):
    accounts = await db.accounts.find({"user": user}).to_list(length=100)
    for a in accounts:
        del a["_id"]
    return accounts


async def refresh_strava_token(user):
    tokens = await db.stravaTokens.find_one({"user": user})
    async with AsyncClient(base_url=Strava.url) as client:
        response = await client.post(
            "/api/v3/oauth/token",
            data={
                "client_id": Strava.id,
                "client_secret": Strava.secret,
                "refresh_token": tokens["refresh_token"],
                "grant_type": "refresh_token",
            },
        )
        data = response.json()

    data["user"] = user
    result = await db.stravaTokens.find_one_and_update(
        {"user": user},
        {"$set": data},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return result


async def get_gear_by_user(user: str):
    tokens = await db.stravaTokens.find_one({"user": user})
    if time.time() > tokens["expires_at"]:
        tokens = await refresh_strava_token(user)

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    async with AsyncClient(base_url=Strava.url + Strava.api, headers=headers) as client:
        response = await client.get("/athlete")
        data = response.json()

    return data["shoes"]


@app.get("/gear_by_user/{user}")
async def get_gear_by_user_endpoint(user: str):
    result = await get_gear_by_user(user)
    return result


class Gear(BaseModel):
    user: str
    id: str
    distance: float
    lifespan: float
    value: float
    savings: float
    name: str


@app.post("/gear/add")
async def add_gear(gear: Gear):
    await db.gears.replace_one({"id": gear.id}, gear.dict(), upsert=True)


@app.get("/shoes/{user}")
async def list_shoes(user: str):
    shoes = await db.gears.find({"user": user}).to_list(length=100)
    for s in shoes:
        del s["_id"]
    return shoes


class Subscription(BaseModel):
    aspect_type: str
    event_time: int
    object_id: int
    object_type: str
    owner_id: int
    subscription_id: int
    updates: Optional[dict]


def list2dict(l, idkey="id"):
    return {o[idkey]: o for o in l}


@app.get("/listen")
async def listen(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):

    if hub_verify_token == Host.verify_token:
        return {"hub.challenge": hub_challenge}


async def delayed_compare(user, delay=1):
    await asyncio.sleep(delay)
    await compare(user)
    print("Completed sync")


async def compare(user="Jan"):
    current = await db.gears.find({"user": user}).to_list(length=100)
    new = await get_gear_by_user(user)
    current = list2dict(current)
    new = list2dict(new)

    transfer_amount = 0
    for k in new:
        if k in current:
            diff = new[k]["converted_distance"] - current[k]["distance"]
            if diff == 0:
                print(f"no change for {k}")
            else:
                left = current[k]["lifespan"] - new[k]["converted_distance"]
                replace = current[k]["value"] - current[k]["savings"]
                m = replace / left
                contrib = m * diff
                await db.gears.update_one(
                    {"id": k}, {"$set": {"distance": new[k]["converted_distance"]}}
                )
                await db.gears.update_one(
                    {"id": k}, {"$set": {"savings": current[k]["savings"] + contrib}}
                )
                transfer_amount += contrib
                if contrib > 0:
                    print(f"transfer {contrib} to savings for {k}")
                elif contrib < 0:
                    print(f"transfer {-1 * contrib} to cheque for {k}")

    accounts = await db.accounts.find({"user": user}).to_list(length=100)
    savings = ""
    cheque = ""
    for a in accounts:
        if a["productName"] == "Cash Management Account":
            savings = a["accountId"]
        elif a["productName"] == "Private Bank Account":
            cheque = a["accountId"]

    print("net transfer:", transfer_amount)
    if transfer_amount > 0:
        await transfer_money(
            user, cheque, savings, transfer_amount, f"Saving for shoes"
        )


async def transfer_money(user, from_account, to_account, amount, reference):
    tokens = await db.investecTokens.find_one({"user": user})

    if time.time() >= tokens["expires_at"]:
        tokens = await refresh_investec_token(user)

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    async with AsyncClient(base_url=Investec.url, headers=headers) as client:
        response = await client.post(
            "/za/pb/v1/accounts/transfermultiple",
            json={
                "AccountId": from_account,
                "TransferList": [
                    {
                        "BeneficiaryAccountId": to_account,
                        "Amount": str(amount),
                        "MyReference": reference,
                        "TheirReference": reference,
                    }
                ],
            },
        )
        data = response.json()
    return data


@app.post("/listen")
async def listen_updates(sub: Subscription, background_tasks: BackgroundTasks):
    if sub.object_type == "activity":
        print("Received: ", sub)
        print("Will sync in 2 minutes")
        background_tasks.add_task(delayed_compare, user="Jan")
    else:
        print(sub)
    return True
