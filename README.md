# x-centis run

## install
Built for heroku. Best installed by creating a heroku app, cloning this repository, setting git remotes to the heroku repo, pushing and deploying the app on heroku. Finally running the dyno. Recommended: use heroku postgres for persistence, heroku scheduler for scheduling the jobs.
Make sure to add the ffmpeg needed for creating the bar chart race video. 

## environment
Needs the following environment variables set:

- `DATABASE_URL` connection string to database
- `STRAVA_WEB_USER` user to log in to Strava website
- `STRAVA_WEB_PWD` password to log in to Strava website
- `STRAVA_API_CLIENTID` Strava API app client id
- `STRAVA_API_CLIENTSECRET` Strava API app client secret
- `STRAVA_OAUTH_REDIRECT` URL to redirect the oauth response to
- `APP_KEY` randomly generated session secret

## configuration
look at `env.py` for a description of configuration options

## scheduled jobs

There are three jobs that should be scheduled to run on a regular basis:

- `sync_club_members` used to access leader boards and grab their member athletes. Proposed cadence: daily.
- `sync_ytd_stats` gets annual distances for every athlete in the database. Should run daily.
- `sync_chart_race_stats` gets the data for - and builds - the bar chart race. Run it once a week.
