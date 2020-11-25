# copied base for login from
# https://github.com/loisaidasam/stravalib-scraper/

from bs4 import BeautifulSoup
import requests


class StravaScraper:

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()

        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"

        self.headers = {'User-Agent': self.user_agent}

        self.base_url = "https://www.strava.com"
        self.login_url = "%s/login" % self.base_url
        self.session_url = "%s/session" % self.base_url
        self.dashboard_url = "%s/dashboard" % self.base_url
        self.leaderboard_url = "{}/clubs/{}/leaderboard"
        self.stats_url = "{}/athletes/{}/profile_sidebar_comparison?ytd_year={}"

    def get_page(self, url):
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_page_xhr(self, url):
        headers = self.headers.copy()
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Accept"] = "text/javascript,application/javascript,application/ecmascript, application/x-ecmascript"

        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response

    def login(self):
        response = self.get_page(self.login_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        utf8 = soup.find_all('input',
                             {'name': 'utf8'})[0].get('value').encode('utf-8')
        token = soup.find_all('input',
                              {'name': 'authenticity_token'})[0].get('value')
        data = {
            'utf8': utf8,
            'authenticity_token': token,
            'plan': "",
            'email': self.email,
            'password': self.password,
        }
        response = self.session.post(self.session_url,
                                     data=data,
                                     headers=self.headers)
        response.raise_for_status()
        response = self.get_page(self.dashboard_url)

    def get_club_leaderboard(self, club_id):
        url = self.leaderboard_url.format(self.base_url, club_id)
        response = self.get_page_xhr(url)
        response.raise_for_status()

        return response.json()["data"]

    def get_athlete_stats(self, athlete_id, year):
        url = self.stats_url.format(self.base_url, athlete_id, year)
        response = self.get_page_xhr(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # hack hack hack
        distance = soup.find(id="running-ytd").find_next("tr").find_all("td")[1].text.replace(" km", "").replace(" mi", "")
        return float(distance.replace(",", ""))
