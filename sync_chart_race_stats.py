from models.ClubMembers import Club, Athlete, ChartRace, ChartRaceCharts
from base import Session, engine, Base
from StravaScraper import StravaScraper
from env import STRAVA_WEB_USER, STRAVA_WEB_PWD, YEAR
from datetime import datetime
import pandas as pd
from sqlalchemy import asc, desc
import numpy as np
import bar_chart_race as bcr


Base.metadata.create_all(engine)
session = Session()


def sync_chart_race_stats():
    calendar = datetime.now().isocalendar()
    if calendar[0] != YEAR:
        return

    current_week = calendar[1]

    response = session.query(ChartRace.week).filter(ChartRace.year == YEAR).distinct().all()
    weeks = [value for (value,) in response]

    scraper = StravaScraper(STRAVA_WEB_USER, STRAVA_WEB_PWD)
    scraper.login()

    # hack hack hack
    club_id = 445835

    for week_offset in range(current_week - 1, 0, -1):
        week_of_year = current_week - week_offset
        if week_of_year in weeks:
            continue

        athletes = scraper.get_club_leaderboard(club_id, week_offset=week_offset)
        add_leaderboard_stats_for_week(YEAR, week_of_year, athletes)

        session.commit()

    session.close()


def add_leaderboard_stats_for_week(year, week, athletes):
    for a in athletes:
        c = ChartRace(a["athlete_id"], year, week, a["distance"])
        session.add(c)


def build_chart_race():
    # hack hack hack
    club_id = 445835

    query = session.query(Athlete.firstname, Athlete.lastname,
                          ChartRace.week, ChartRace.year, ChartRace.distance, Club.id)\
        .filter(ChartRace.year == YEAR)\
        .filter(Club.id == club_id)\
        .join(Athlete)\
        .join(Club, Athlete.clubs)\
        .group_by(Athlete.id, ChartRace.week, ChartRace.year, ChartRace.distance, Club.id)\
        .order_by(asc(ChartRace.week), desc(ChartRace.distance))

    df = pd.read_sql(query.statement, query.session.bind)
    df["name"] = df["firstname"] + " " + df["lastname"]
    df.drop(columns=["firstname", "lastname", "year", "id"], inplace=True)

    table = pd.pivot_table(df, values='distance', index=['week'],
                           columns=['name'], aggfunc=np.sum, fill_value=0)
    cumsum_table = table.cumsum()

    html = bcr.bar_chart_race(
        df=cumsum_table,
        filename=None,
        title='Race to ' + str(YEAR),
        period_fmt='Week {x:,.0f}',
        period_summary_func=chart_summary
    )

    record = session.query(ChartRaceCharts)\
        .filter(ChartRaceCharts.club_id == club_id)\
        .filter(ChartRaceCharts.year == YEAR)\
        .first()

    if not record:
        record = ChartRaceCharts(club_id, YEAR, html)
        session.add(record)
    else:
        record.video_html = html

    session.commit()
    session.close()


def chart_summary(values, ranks):
    total_m = int(round(values.sum(), -2))
    s = f'Total [m] - {total_m:,.0f}'
    return {'x': .99, 'y': .05, 's': s, 'ha': 'right', 'size': 8}


if __name__ == '__main__':
    sync_chart_race_stats()
    build_chart_race()