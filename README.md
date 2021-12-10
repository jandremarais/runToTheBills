# runToTheBills
My Investec 2021 Q4 Transfer API Hackathon submission


## Setup

**Note: some of these instructions are old and need to be updated.**

In addition the the Investec Transfer API, you'll need access the a [Strava developer account](https://developers.strava.com/docs/getting-started/).

Place the Investec and Strava secrets in an `.env` file:

```
verify_token="xxx"
strava_client_id= "xxx"
strava_client_secret= "xxx"
```

Prepare your python environment with (need [poetry](https://developers.strava.com/docs/getting-started/)):

```
poetry install
```

Run the server with:
```
poetry run uvicorn main:app
```

and if running locally,  expose a port with:

```
ngrok http 8000
```

Create a Strava subscription by running `utils.subscribe()` in a new python process.

Then watch the updates come in.
