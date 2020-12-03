from flask import Flask, request, redirect, session, render_template
from flask_bootstrap import Bootstrap
import os
from env import STRAVA_API_CLIENTID, STRAVA_API_CLIENTSECRET, YEAR, STRAVA_OAUTH_REDIRECT, APP_KEY
import requests
from base import Session
from models.ClubMembers import Club, Stats, Athlete
from sqlalchemy import desc
from StravaAPI import StravaAPI

app = Flask(__name__)
app.secret_key = APP_KEY
Bootstrap(app)

dbsession = Session()


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
                    "&redirect_uri={}"
                    "&scope=read"
                    "&approval_prompt=auto".format(STRAVA_API_CLIENTID, STRAVA_OAUTH_REDIRECT))


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    # hack, hardcoded, provide selection in the future
    club = "445835"

    user = None
    if session.get('user') is None or session.get('access_token') is None:
        return redirect("/")
    user = session['user']

    api = StravaAPI(session["access_token"])
    clubs = api.get_clubs()

    # only return stats if the person is a member of the (currently) hardcoded club
    stats = []
    if next((c for c in clubs if str(c["id"]) == club), False):
        stats = dbsession.query(Athlete)\
            .join(Stats, Athlete.stats)\
            .join(Club, Athlete.clubs)\
            .filter(Club.id == club)\
            .filter(Stats.year == YEAR)\
            .order_by(desc(Stats.running_ytd_distance))\
            .all()

    return render_template('leaderboard.html', stats_list=stats, user=user)


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
    else:
        print(r.text)

    return redirect('/')


if __name__ == '__main__':
    app.run()
