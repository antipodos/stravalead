from models.ClubMembers import Club, Athlete
from base import Session, engine, Base
from StravaScraper import StravaScraper
from env import CLUB_IDS, STRAVA_WEB_USER, STRAVA_WEB_PWD, YEAR

Base.metadata.create_all(engine)
session = Session()


def sync_club_members():
    scraper = StravaScraper(STRAVA_WEB_USER, STRAVA_WEB_PWD)
    scraper.login()

    for club_id in CLUB_IDS:
        club = session.query(Club).filter(Club.id == club_id).first()
        if not club:
            club = Club(club_id)
            session.add(club)

        athletes = scraper.get_club_leaderboard(club_id)

        for a in athletes:
            athlete = session.query(Athlete).filter(Athlete.id == a["athlete_id"]).first()

            if not athlete:
                athlete = Athlete(a["athlete_id"], a["athlete_firstname"], a["athlete_lastname"])
                session.add(athlete)

            if athlete not in club.athletes:
                club.athletes.append(athlete)

    session.commit()
    session.close()


if __name__ == '__main__':
    sync_club_members()
