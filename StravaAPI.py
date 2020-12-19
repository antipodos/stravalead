import requests


class StravaAPI:

    def __init__(self, access_token):
        self.access_token = access_token
        self.baseURL = "https://www.strava.com/"

    @staticmethod
    def get_access_token(client_id, api_secret, code):
        params = {
            "client_id": client_id,
            "client_secret": api_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        r = requests.post("https://www.strava.com/oauth/token", params)

        if r.status_code == 200:
            return r.json()
        else:
            return None

    def get_headers(self):
        return { "Authorization": "Bearer {}".format(self.access_token) }

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
