import requests
from time import time


class StravaAPI:

    def __init__(self, client_id, api_secret, access_token=None, refresh_token=None, expires_at=None):
        self.client_id = client_id
        self.api_secret = api_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        self.baseURL = "https://www.strava.com/"

    def is_access_token_expired(self):
        if self.expires_at is None:
            return False

        return self.expires_at < time()

    def refresh_access_token(self):
        if self.refresh_token is None:
            return

        params = {
            "client_id": self.client_id,
            "client_secret": self.api_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        r = requests.post("https://www.strava.com/oauth/token", params)

        if r.status_code == 200:
            response = r.json()

            self.access_token = response["access_token"]
            self.expires_at = time() + response["expires_in"]
            self.refresh_token = response["refresh_token"]

    def get_access_token(self, code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.api_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        r = requests.post("https://www.strava.com/oauth/token", params)
        response = r.json()

        if r.status_code == 200:
            self.access_token = response["access_token"]
            self.expires_at = time() + response["expires_in"]
            self.refresh_token = response["refresh_token"]

            return response["athlete"]
        else:
            return None

    def get_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def get_clubs(self):
        endpoint = "api/v3/athlete/clubs"

        response = self.api_call(endpoint)
        try:
            return response.json()
        except:
            return None

    def api_call(self, endpoint, page=1, per_page=200):
        headers = self.get_headers()

        response = requests.get(self.baseURL
                                + endpoint
                                + "?page=" + str(page)
                                + "&per_page=" + str(per_page),
                                headers=headers)

        if response.status_code != 200:
            return None

        return response
