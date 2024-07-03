import requests

import dotenv
from os import getenv, environ

from time import time

try:
    from models.api import statsUrls
except:
    import statsUrls


class StatsInterface:

    def __init__(self, app_id, key) -> None:
        self.dotenv_file = dotenv.find_dotenv()

        self.app_id = app_id
        self.key = key

        self.auth_token: dict = None
        self.refresh_token: dict = None
        self.app: dict = None

    def fetch_auth_token(self, app_id: str, key: str) -> bool:
        """Get authentification tokens from the API for current session to make further requests

        Args:
            app_id (str): Application id
            key (str): Secret api key

        Returns:
            bool: True if connection was successfull otherwise False
        """

        r = requests.post(statsUrls.BASE_URL + statsUrls.GET_TOKEN, headers={'Content-Type': 'application/json'}, json={"app_id": app_id, "api_key": key})

        if r.status_code == 200:
            data = r.json()
            self.write_tokens(data["access_token"],
                              data["refresh_token"], app=data["app"])
            return True
        else:
            raise ConnectionRefusedError(
                f"Fetch token responded with a {r.status_code}")

    def refresh_auth_token(self) -> bool:
        self.fetch_auth_token(self.app_id, self.key)
        return
        r = requests.get(statsUrls.BASE_URL + statsUrls.GET_REFRESH_TOKEN, headers={'Content-Type': 'application/json', "X-Refresh-Token": self.refresh_token["token"]})
        
        if r.status_code == 200:
            data = r.json()
            self.write_tokens(data["access_token"],
                              data["refresh_token"])
            return True
        else:
            print(ConnectionRefusedError(
                f"Fetch token responded with a {r.status_code}, fetching new tokens"))
            self.fetch_auth_token(self.app_id, self.key)


    def should_refresh(self) -> bool:
        if int(self.auth_token["expires_at"]) < int(time() + 86400):
            return True
        return False

    def get_api(self, url: str, path_parameters: dict = None, query_payload: dict = None) -> requests.Response:
        """Make a GET to the API

        Args:
            url (str): Ressource's URL to retreive
            query_payload (dict, optional): Query data to filter the GET. Defaults to None.

        Raises:
            response.status_code: HTTP Code if the API sent anything else than 200

        Returns:
            json: API Response when request is 200
        """
        if self.should_refresh():
            self.refresh_auth_token()
        
        if (path_parameters != None):
            response = requests.get(
                statsUrls.BASE_URL + url.format(**path_parameters), headers={'Content-Type': 'application/json', "X-Access-Token": self.auth_token["token"]}, params=query_payload)
        else:
            response = requests.get(
                statsUrls.BASE_URL + url, headers={'Content-Type': 'application/json', "X-Access-Token": self.auth_token["token"]}, params=query_payload)
        return response

    def post_api(self, url: str, payload: dict) -> requests.Response:
        """Make a POST to the API

        Args:
            url (str): Ressource's URL to send
            payload (dict): Data to send

        Raises:
            response.status_code: HTTP Code if the API sent anything else than 200

        Returns:
            json: API Response when request is 200
        """
        if self.should_refresh():
            self.refresh_auth_token()
            
        return requests.post(
            statsUrls.BASE_URL + url, headers={'Content-Type': 'application/json', "X-Access-Token":  self.auth_token["token"]}, json=payload)

    def put_api(self, url: str, path_payload: dict = None, data_payload: dict = None) -> requests.Response:
        """Make a PUT to the API

        Args:
            url (str): Ressource's URL to edit
            path_payload (dict, optional): Path parameters to send in the URL. Defaults to None.
            data_payload (dict, optional): Data to edit. Defaults to None.

        Raises:
            response.status_code: HTTP Code if the API sent anything else than 200

        Returns:
            json: API Response when request is 200
        """
        if self.should_refresh():
            self.refresh_auth_token()

        response = requests.put(
            statsUrls.BASE_URL + url, headers={'Content-Type': 'application/json', "X-Access-Token": self.auth_token["token"]}, params=path_payload, data=data_payload)
        return response

    def delete_api(self, url: str, path_payload: dict = None) -> requests.Response:
        if self.should_refresh():
            self.refresh_auth_token()
            
        if path_payload != None:
            return requests.delete(statsUrls.BASE_URL + url.format(**path_payload), headers={'Content-Type': 'application/json', "X-Access-Token": self.auth_token["token"]})
        else:
            return requests.delete(statsUrls.BASE_URL + url, headers={'Content-Type': 'application/json', "X-Access-Token": self.auth_token["token"]})

    def write_tokens(self, access_token, refresh_token, app = None):
        self.auth_token = access_token
        self.refresh_token = refresh_token
        if app != None:
            self.app = app

        environ["STATS_USER_TOKEN"] = str(access_token["token"])
        environ["STATS_USER_TOKEN_EXPIRATION"] = str(access_token["expires_at"])

        environ["STATS_USER_REFRESH_TOKEN"] = str(refresh_token["token"])
        environ["STATS_USER_REFRESH_TOKEN_EXPIRATION"] = str(
            refresh_token["expires_at"])

        dotenv.set_key(self.dotenv_file, "STATS_USER_TOKEN",
                       environ["STATS_USER_TOKEN"])
        dotenv.set_key(self.dotenv_file, "STATS_USER_TOKEN_EXPIRATION",
                       environ["STATS_USER_TOKEN_EXPIRATION"])

        dotenv.set_key(self.dotenv_file, "STATS_USER_REFRESH_TOKEN",
                       environ["STATS_USER_REFRESH_TOKEN"])
        dotenv.set_key(self.dotenv_file, "STATS_USER_REFRESH_TOKEN_EXPIRATION",
                       environ["STATS_USER_REFRESH_TOKEN_EXPIRATION"])

        print("[INFO] Write tokens OK")

    def read_tokens(self):
        self.auth_token = {
            'token': getenv("STATS_USER_TOKEN"),
            'expires_at': getenv("STATS_USER_TOKEN_EXPIRATION")
        }

        self.refresh_token = {
            'token': getenv("STATS_USER_REFRESH_TOKEN"),
            'expires_at': getenv("STATS_USER_REFRESH_TOKEN_EXPIRATION")
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()

    stats_log = getenv("STATS_PARKKI_ID")
    stats_token = getenv("STATS_PARKKI_TOKEN")

    stats = StatsInterface()
    stats.read_tokens()
    stats.fetch_auth_token(stats_log, stats_token)
    
    contract = None

    r = stats.get_api(statsUrls.GET_CONTRACTS)
    #print(r, r.json())
    for c in r.json():
        if c["name"] == "Humanicité":
            contract = c
            break
    
    r = stats.get_api(statsUrls.GET_AREAS, query_payload={'contract_id': contract['id']})
    #print(curlify.to_curl(r.request))
    print(r)
    #print(r.json())


    areas = r.json()["areas"]
    print([(a['id'], a['long_name'], a['type']) for a in areas])
    for a in areas:
        if a['type'] == 'PARKANDFLOW':
            aid = a['id']
    
    """r = stats.post_api(statsUrls.GET_PARKED_CARS, payload={'timestamp': 1687869036, 'areas': [aid]})
    print(r)
    print(r.json())"""
    r = stats.post_api(statsUrls.GET_GENERAL_STATS_OF_PARKING, payload={'timestamp': 1687869187, 'areas':[aid]})
    print(r, r.text)
    if r.status_code == 200:
        print(r.json())
