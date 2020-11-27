import requests


class StravaAPI:

    def __init__(self, access_token):
        self.access_token = access_token
        self.baseURL = "https://www.strava.com/"

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
