from models.ClubMembers import Club, Athlete
from base import Session, engine, Base
from StravaScraper import StravaScraper
from env import CLUB_IDS, STRAVA_WEB_USER, STRAVA_WEB_PWD, WEEK_OFFSET_RANGE

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

        for week_offset in range(0, WEEK_OFFSET_RANGE):
            athletes = scraper.get_club_leaderboard(club_id, week_offset=week_offset)
            update_athletes(club, athletes)

    session.commit()
    session.close()


def update_athletes(club, athletes):
    for a in athletes:
        athlete = session.query(Athlete).filter(Athlete.id == a["athlete_id"]).first()

        if not athlete:
            athlete = Athlete(a["athlete_id"], a["athlete_firstname"], a["athlete_lastname"])
            session.add(athlete)
        else:
            athlete.firstname = a["athlete_firstname"]
            athlete.lastname = a["athlete_lastname"]

        if athlete not in club.athletes:
            club.athletes.append(athlete)


if __name__ == '__main__':
    sync_club_members()
