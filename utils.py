from dataclasses import dataclass
import os
from dotenv import load_dotenv
from httpx import Client
import json
from pathlib import Path
import time
# from datetime import datetime


load_dotenv()


@dataclass
class Host:
    url: str = "http://localhost:8000"
    verify_token: str = os.environ["verify_token"]


@dataclass
class Strava:
    url: str = "https://www.strava.com"
    api: str = "/api/v3"
    id: str = os.environ["strava_client_id"]
    secret: str = os.environ["strava_client_secret"]


@dataclass
class Investec:
    url: str = "https://openapi.investec.com"
    id: str = os.environ['investec_client_id']
    secret: str = os.environ['investec_client_secret']


def get_strava_auth_url():
    scope = "read,activity:read_all,profile:read_all"
    redirect_url = (
        f"{Host.url}/strava/exchange_token&approval_prompt=force&scope={scope}"
    )
    auth_url = f"{Strava.url}/oauth/authorize?client_id={Strava.id}&response_type=code&redirect_uri={redirect_url}"
    return auth_url


@dataclass
class Investec:
    url: str = "https://openapi.investec.com"
    id: str = os.environ["investec_client_id"]
    secret: str = os.environ["investec_client_secret"]
    current: str = os.environ["investec_current"]
    savings: str = os.environ["investec_savings"]


# def refresh_token():
#     with open("strava_token.json", "r") as fp:
#         token_data = json.load(fp)
#     with Client(base_url=Strava.url) as client:
#         response = client.post(
#             "/api/v3/oauth/token",
#             data={
#                 "client_id": Strava.id,
#                 "client_secret": Strava.secret,
#                 "refresh_token": token_data["refresh_token"],
#                 "grant_type": "refresh_token",
#             },
#         )
#         data = response.json()
#         token_data.update(
#             {k: data[k] for k in ["expires_at", "refresh_token", "access_token"]}
#         )
#         with open("strava_token.json", "w") as fp:
#             json.dump(data, fp)


# def get_shoes():
#     with open("strava_token.json", "r") as fp:
#         token_data = json.load(fp)
#     headers = {"Authorization": f"Bearer {token_data['access_token']}"}
#     with Client(base_url=Strava.url + Strava.api, headers=headers) as client:
#         response = client.get("/athlete")
#         data = response.json()
    
#     return data['shoes']
        # with open("shoes.json", "w") as fp:
            # json.dump(data["shoes"], fp, indent=2)


# def init_savings():
#     shoes = read_shoes()

#     savings = read_savings()

#     savings_ids = set([o["id"] for o in savings])

#     for shoe in shoes:
#         if shoe["id"] not in savings_ids:
#             savings.append(
#                 {"id": shoe["id"], "value": 0, "contributions": 0, "lifespan": 0}
#             )

#     with open("savings.json", "w") as fp:
#         json.dump(savings, fp, indent=2)


# def read_shoes():
#     try:
#         with open("shoes.json", "r") as fp:
#             shoes = json.load(fp)
#     except FileNotFoundError:
#         shoes = []
#     return shoes


# def read_savings():
#     try:
#         with open("savings.json", "r") as fp:
#             savings = json.load(fp)
#     except FileNotFoundError:
#         savings = []
#     return savings

def load_tokens():
    with open("strava_token.json", "r") as fp:
        tokens = json.load(fp)
    return tokens


def refresh_token(token: str):
    with Client(base_url=Strava.url) as client:
        response = client.post(
            "/api/v3/oauth/token",
            data={
                "client_id": Strava.id,
                "client_secret": Strava.secret,
                "refresh_token": token,
                "grant_type": "refresh_token",
            },
        )
    return response.json()


def load_tokens_with_refresh():
    tokens = load_tokens()
    if time.time() > tokens['expires_at']:
        tokens = refresh_token(tokens['refresh_token'])
        with open("strava_token.json", "w") as fp:
            json.dump(tokens, fp)
    return tokens


def create_header(tokens: dict):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def list2dict(l, idkey='id'):
    return {o[idkey]: o for o in l}


def get_shoes():
    tokens = load_tokens_with_refresh()
    headers = create_header(tokens)
    with Client(base_url=Strava.url + Strava.api, headers=headers) as client:
        response = client.get('/athlete')
        data = response.json()
    return data['shoes']


def read_shoes():
    with open("shoes.json", "r") as fp:
        shoes = json.load(fp)
    return shoes


def write_shoes(shoes):
    with open("shoes.json", 'w') as fp:
        json.dump(shoes, fp, indent=2)


def sync_shoes():
    shoes = get_shoes()
    shoes = list2dict(shoes)
    write_shoes(shoes)


def read_savings():
    with open("savings.json", "r") as fp:
        savings = json.load(fp)
    return savings

def write_savings(savings):
    with open("savings.json", 'w') as fp:
        json.dump(savings, fp, indent=2)


def load_investec_tokens():
    with open("investec_token.json", "r") as fp:
        tokens = json.load(fp)
    return tokens


def refresh_investec_token():
    with Client(base_url=Investec.url, auth=(Investec.id, Investec.secret)) as client:
        response = client.post(
            "/identity/v2/oauth2/token",
            data={
                "scope": "accounts",
                "grant_type": "client_credentials",
            },
        )
        data = response.json()
    data["expires_at"] = time.time() + data["expires_in"]
    return data


def load_investec_tokens_with_refresh():
    tokens = load_investec_tokens()
    if time.time() > tokens["expires_at"]:
        tokens = refresh_investec_token()
        with open("investec_token.json", "w") as fp:
            json.dump(tokens, fp, indent=2)
    return tokens


def get_account():
    tokens = load_investec_tokens_with_refresh()
    headers = create_header(tokens)
    with Client(base_url=Investec.url, headers=headers) as client:
        response = client.get("/za/pb/v1/accounts")
        data = response.json()
    return data["data"]


# from_account = Investec.current
# to_account = Investec.savings
# amount = 10.0
# reference = "Test"

def transfer_money(from_account, to_account, amount, reference):
    tokens = load_investec_tokens_with_refresh()
    headers = create_header(tokens)
    with Client(base_url=Investec.url, headers=headers) as client:
        response = client.post(
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


def compare():
    current = read_shoes()
    new = get_shoes()
    new = list2dict(new)

    savings = read_savings()

    transfer_amount = 0
    for k in new:
        if k in savings:
            diff = new[k]['converted_distance'] - current[k]['converted_distance']
            if diff == 0:
                print(f"no change for {k}")
            else:
                left = savings[k]['lifespan'] - new[k]['converted_distance']
                replace = savings[k]['value'] - savings[k]['contributions']
                m = replace / left
                contrib = m * diff
                savings[k]['contributions'] += contrib
                transfer_amount += contrib
                if contrib > 0:
                    print(f"transfer {contrib} to savings for {k}")
                elif contrib < 0:
                    print(f"transfer {-1 * contrib} to cheque for {k}")
    
    transfer_money(Investec.current, Investec.savings, transfer_amount, f"Saving for shoes")
    print("net transfer:", transfer_amount)
    write_savings(savings)
    write_shoes(new)



def subscribe():
    with Client(base_url=Strava.url + Strava.api) as client:
        response = client.post(
            "/push_subscriptions",
            data={
                "client_id": Strava.id,
                "client_secret": Strava.secret,
                "callback_url": f" http://4e22-41-114-211-65.ngrok.io/listen",
                "verify_token": Host.verify_token,
            },
        )
        data = response.json()
    return data


def list_subscriptions():
    with Client(base_url=Strava.url + Strava.api) as client:
        response = client.get(
            "/push_subscriptions",
            params={"client_id": Strava.id, "client_secret": Strava.secret},
        )
        print(response.json())


def delete_subscriptions(id: int):
    with Client(base_url=Strava.url + Strava.api) as client:
        response = client.delete(
            f"/push_subscriptions/{str(id)}",
            params={"client_id": Strava.id, "client_secret": Strava.secret},
        )
        print(response)