import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

STRAVA_WEB_USER = os.getenv("STRAVA_WEB_USER")
STRAVA_WEB_PWD = os.getenv("STRAVA_WEB_PWD")
STRAVA_API_CLIENTID = os.getenv("STRAVA_API_CLIENTID")
STRAVA_API_CLIENTSECRET = os.getenv("STRAVA_API_CLIENTSECRET")

APP_KEY = os.getenv("APP_KEY")

STRAVA_OAUTH_REDIRECT = os.getenv("STRAVA_OAUTH_REDIRECT")

# list of clubs to build leaderboards for
CLUB_IDS = [445835, 792660]

# set this to any year to build an annual leaderboard for that specific year
YEAR = datetime.now().year

# set this to 1 to scrape just the current week
# set to a higher number if you want to iterate back in time and scrape many weeks' worth of leaderboards
# as scraping leaderboards is used to build the set of club members, it could make sense to run the script once
# with a larger range, then set back to 1 (as it will persist the members anyways)
WEEK_OFFSET_RANGE = 1
