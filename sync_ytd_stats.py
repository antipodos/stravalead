from models.ClubMembers import Athlete, Stats
from base import Session, engine, Base
from StravaScraper import StravaScraper
from env import STRAVA_WEB_USER, STRAVA_WEB_PWD, YEAR

Base.metadata.create_all(engine)
session = Session()


def sync_ytd_stats():
    print("syncing statistics")

    athletes = session.query(Athlete).all()

    scraper = StravaScraper(STRAVA_WEB_USER, STRAVA_WEB_PWD)
    scraper.login()

    for athlete in athletes:
        distance = scraper.get_athlete_stats(athlete.id, YEAR)

        stats = session.query(Stats).filter(Stats.athlete_id == athlete.id and Stats.year == YEAR).first()
        if not stats:
            stats = Stats(athlete.id, YEAR, distance)
            session.add(stats)
        else:
            stats.running_ytd_distance = distance

        athlete.set_update_timestamp()

    session.commit()
    session.close()


if __name__ == '__main__':
    sync_ytd_stats()
