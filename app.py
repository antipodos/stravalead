from flask import g, Flask, request, redirect, session, render_template, url_for
from flask_bootstrap import Bootstrap
from env import STRAVA_API_CLIENTID, STRAVA_API_CLIENTSECRET, YEAR, STRAVA_OAUTH_REDIRECT, APP_KEY
from base import Session
from models.ClubMembers import Club, Stats, Athlete
from sqlalchemy import desc
from StravaAPI import StravaAPI
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, login_url
from User import User

app = Flask(__name__)
app.secret_key = APP_KEY
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "authorize"

dbsession = Session()


@login_manager.user_loader
def load_user(user_id):
    user = User(user_id)
    if "user" in session:
        if session["user"]["id"] == user_id:
            user.firstname = session["user"]["firstname"]
            user.authenticated = True
    return user


@app.route("/", methods=["GET"])
def web_home():
    return render_template('index.html')


@app.route("/authorize", methods=["GET"])
def authorize():
    next_url = request.args.get("next") if "next" in request.args else "/"
    return redirect("https://www.strava.com/oauth/authorize?"
                    "client_id={}"
                    "&response_type=code"
                    "&redirect_uri={}"
                    "&scope=read"
                    "&approval_prompt=auto".format(STRAVA_API_CLIENTID, STRAVA_OAUTH_REDIRECT
                                                   + "?next="
                                                   + next_url))


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    session.pop("user")
    return redirect("/")


@app.route("/leaderboard", methods=["GET"])
@login_required
def leaderboard():
    # hack, hardcoded, provide selection in the future
    club = "445835"

    api = StravaAPI(STRAVA_API_CLIENTID,
                    STRAVA_API_CLIENTSECRET,
                    session["access_token"],
                    session["refresh_token"],
                    session["access_token_expires_at"])

    if api.is_access_token_expired():
        api.refresh_access_token()
        session["access_token"] = api.access_token
        session["refresh_token"] = api.refresh_token
        session["access_token_expires_at"] = api.expires_at

    clubs = api.get_clubs()

    # only return stats if the person is a member of the (currently) hardcoded club
    stats = []

    if clubs is not None:
        if next((c for c in clubs if str(c["id"]) == club), False):
            stats = dbsession.query(Athlete)\
                .join(Stats, Athlete.stats)\
                .join(Club, Athlete.clubs)\
                .filter(Club.id == club)\
                .filter(Stats.year == YEAR)\
                .order_by(desc(Stats.running_ytd_distance))\
                .all()

    return render_template('leaderboard.html', stats_list=stats)


@app.route("/oauth", methods=["GET"])
def exchange_token():
    access = request.args.get('code')
    if access == "error":
        redirect("/error")

    code = request.args.get('code')

    api = StravaAPI(STRAVA_API_CLIENTID, STRAVA_API_CLIENTSECRET)
    athlete = api.get_access_token(code)

    if api.access_token is not None:
        session["access_token"] = api.access_token
        session["access_token_expires_at"] = api.expires_at
        session["refresh_token"] = api.refresh_token
        session["user"] = athlete
        u = User(athlete["id"])
        u.authenticated = True
        login_user(u, remember=True)
    else:
        print("Error while processing oauth request")

    next_url = request.args.get("next") if "next" in request.args else "/"
    return redirect(next_url)


if __name__ == '__main__':
    app.run()
