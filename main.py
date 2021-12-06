import json
import time
from typing import Optional

import httpx
from fastapi import (BackgroundTasks, FastAPI, Form, HTTPException, Query,
                     Request)
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient
from pydantic import BaseModel
from starlette.responses import HTMLResponse

from utils import Host, Strava, compare, get_shoes, read_savings, read_shoes

app = FastAPI(title="Run to the Hills")

templates = Jinja2Templates("templates")


@app.get("/strava/exchange_token")
async def strava_exchange_token(scope: str, code: str, state: str):
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
        token_data = {
            k: data[k] for k in ["expires_at", "refresh_token", "access_token"]
        }
        token_data["athlete"] = data["athlete"]["id"]
        with open("strava_token.json", "w") as fp:
            json.dump(data, fp)


# @app.get("/summary", response_class=HTMLResponse)
# def summary(request: Request):
#     savings = read_savings()
#     shoes = read_shoes()
#     for shoe in shoes:
#         for saving in savings:
#             if saving["id"] == shoe["id"]:
#                 shoe.update(saving)
#     return templates.TemplateResponse(
#         "index.html", {"request": request, "shoes": shoes}
#     )


# @app.put("/savings/update/{item_id}")
# def savings_update(item_id: str, value: int = Form(...), lifespan: int = Form(...)):
#     # print(data)
#     savings = read_savings()
#     for saving in savings:
#         if saving["id"] == item_id:
#             saving.update({"lifespan": lifespan, "value": value})

#     with open("savings.json", "w") as fp:
#         json.dump(savings, fp, indent=2)


class Subscription(BaseModel):
    aspect_type: str
    event_time: int
    object_id: int
    object_type: str
    owner_id: int
    subscription_id: int
    updates: Optional[dict]


@app.get("/listen")
async def listen(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):

    if hub_verify_token == Host.verify_token:
        return {"hub.challenge": hub_challenge}


def tmp():
    time.sleep(15)
    print('completed')


def delayed_compare(delay=120):
    time.sleep(delay)
    compare()
    print("Completed sync")


@app.post("/listen")
async def listen_updates(sub: Subscription, background_tasks: BackgroundTasks):
    if sub.object_type == 'activity':
        print("Received: ", sub)
        print("Will sync in 2 minutes")
        background_tasks.add_task(delayed_compare)
    else:
        print(sub)
    return True
