import os
from dataclasses import dataclass
from httpx import Client
from dotenv import load_dotenv

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



def subscribe(url):
    with Client(base_url=Strava.url + Strava.api) as client:
        response = client.post(
            "/push_subscriptions",
            data={
                "client_id": Strava.id,
                "client_secret": Strava.secret,
                "callback_url": url,
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