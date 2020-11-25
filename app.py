from flask import Flask, request, redirect, session, render_template
from flask_bootstrap import Bootstrap
import os
from env import STRAVA_API_CLIENTID, STRAVA_API_CLIENTSECRET
import requests
from base import Session
from models.ClubMembers import Club

app = Flask(__name__)

session = Session()


@app.route("/", methods=["GET"])
def web_home():
    user = None
    if session.get('user') is not None:
        user = session['user']
    return render_template('index.html', user=user)


@app.route("/authorize", methods=["GET"])
def authorize():
    return redirect("https://www.strava.com/oauth/authorize?"
                    "client_id={}"
                    "&response_type=code"
                    "&redirect_uri=http://localhost:5000/oauth"
                    "&scope=read"
                    "&approval_prompt=force".format(STRAVA_API_CLIENTID))


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    pass


@app.route("/oauth", methods=["GET"])
def exchange_token():
    access = request.args.get('code')
    if access == "error":
        redirect("/error")

    code = request.args.get('code')

    params = {
        "client_id": STRAVA_API_CLIENTID,
        "client_secret": STRAVA_API_CLIENTSECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    r = requests.post("https://www.strava.com/oauth/token", params)

    if r.status_code == 200:
        result = r.json()
        session["access_token"] = result["access_token"]
        session["user"] = result["athlete"]

    return redirect('/')


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    Bootstrap(app)
    app.run()
