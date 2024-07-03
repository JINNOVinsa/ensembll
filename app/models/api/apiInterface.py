import requests

import dotenv
from os import getenv, environ
from time import time

try:
    from models.api import apiUrls
except:
    try:
        from api import apiUrls
    except:
        import apiUrls


class APIinterface:

    def __init__(self, mail, pswd) -> None:
        self.dotenv_file = dotenv.find_dotenv()

        self.mail = mail
        self.pswd = pswd

        self.auth_token: dict = None
        self.refresh_token: dict = None
        self.user: dict = None
        self.contract:dict = None

    def fetch_auth_token(self, mail: str, pswd: str) -> bool:
        """Get authentification tokens from the API for current session to make further requests

        Args:
            mail (str): Email used for login
            pswd (str): Password used for login

        Returns:
            bool: True if connection was successfull otherwise False
        """

        r = requests.post(apiUrls.BASE_URL + apiUrls.GET_TOKEN,
                          data={"email": mail, "password": pswd})
        if r.status_code == 200:
            data = r.json()
            self.write_tokens(data["access_token"],
                              data["refresh_token"], data["user"])
            return True
        else:
            raise ConnectionRefusedError(
                f"Fetch token responded with a {r.status_code}")

    def refresh_auth_token(self) -> bool:
        r = requests.get(apiUrls.BASE_URL + apiUrls.GET_REFRESH_TOKEN, headers={"Authorization": "Bearer " + self.refresh_token["token"]})
        if r.status_code == 200:
            data = r.json()
            self.write_tokens(data["access_token"],
                              data["refresh_token"])
            return True
        else:
            print(ConnectionRefusedError(
                f"Fetch token responded with a {r.status_code}, fetching new tokens"))
            self.fetch_auth_token(self.mail, self.pswd)

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
                apiUrls.BASE_URL + url.format(**path_parameters), headers={"Authorization": "Bearer " + self.auth_token["token"]}, params=query_payload)
        else:
            response = requests.get(
                apiUrls.BASE_URL + url, headers={"Authorization": "Bearer " + self.auth_token["token"]}, params=query_payload)
        return response

    def post_api(self, url: str, payload: dict = None, path_payload: dict = None) -> requests.Response:
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
        
        if path_payload != None:
            r = requests.post(
                apiUrls.BASE_URL + url.format(**path_payload), headers={"Authorization": "Bearer " + self.auth_token["token"]}, json=payload)
        else:
            r = requests.post(
                apiUrls.BASE_URL + url, headers={"Authorization": "Bearer " + self.auth_token["token"]}, json=payload)
        return r

    def put_api(self, url: str, path_payload: dict = None, data_payload: dict = None) -> requests.Response:
        """Make a PUT to the API

        Args:
            url (str): Ressource's URL to edit
            path_payload (dict, optional): Path parameters to send in the URL. Defaults to None.
            data_payload (dict, optional): Data to edit. Defaults to None. Must contains contract id

        Raises:
            response.status_code: HTTP Code if the API sent anything else than 200

        Returns:
            json: API Response when request is 200
        """
        if self.should_refresh():
            self.refresh_auth_token()
        response = requests.put(
            apiUrls.BASE_URL + url.format(**path_payload), headers={"Authorization": "Bearer " + self.auth_token["token"]}, json=data_payload)
        return response

    def delete_api(self, url: str, path_payload: dict = None) -> requests.Response:
        if self.should_refresh():
            self.refresh_auth_token()
        if path_payload != None:
            return requests.delete(apiUrls.BASE_URL + url.format(**path_payload), headers={"Authorization": "Bearer " + self.auth_token["token"]})
        else:
            return requests.delete(apiUrls.BASE_URL + url, headers={"Authorization": "Bearer " + self.auth_token["token"]})

    def write_tokens(self, access_token, refresh_token, user=None):
        self.auth_token = access_token
        self.refresh_token = refresh_token
        if user != None:
            self.user = user

        environ["API_USER_TOKEN"] = str(access_token["token"])
        environ["API_USER_TOKEN_EXPIRATION"] = str(access_token["expires_at"])

        environ["API_USER_REFRESH_TOKEN"] = str(refresh_token["token"])
        environ["API_USER_REFRESH_TOKEN_EXPIRATION"] = str(
            refresh_token["expires_at"])

        dotenv.set_key(self.dotenv_file, "API_USER_TOKEN",
                       environ["API_USER_TOKEN"])
        dotenv.set_key(self.dotenv_file, "API_USER_TOKEN_EXPIRATION",
                       environ["API_USER_TOKEN_EXPIRATION"])

        dotenv.set_key(self.dotenv_file, "API_USER_REFRESH_TOKEN",
                       environ["API_USER_REFRESH_TOKEN"])
        dotenv.set_key(self.dotenv_file, "API_USER_REFRESH_TOKEN_EXPIRATION",
                       environ["API_USER_REFRESH_TOKEN_EXPIRATION"])

        print("[INFO] Write tokens OK")

    def read_tokens(self):
        self.auth_token = {
            'token': getenv("API_USER_TOKEN"),
            'expires_at': getenv("API_USER_TOKEN_EXPIRATION")
        }

        self.refresh_token = {
            'token': getenv("API_USER_REFRESH_TOKEN"),
            'expires_at': getenv("API_USER_REFRESH_TOKEN_EXPIRATION")
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv
    import apiUrls

    load_dotenv()

    api_id = getenv("API_PARKKI_ID")
    api_log = getenv("API_PARKKI_LOG")
    api_token = getenv("API_PARKKI_TOKEN")

    api = APIinterface()
    api.read_tokens()

    #print(api.get_api(apiUrls.GET_ACCESSES).json())
    print(api.get_api(apiUrls.GET_USERS).json()['users'][1])
    #print(api.delete_api(apiUrls.DELETE_USER, path_payload={'id':'64773d5b10f6ac57b071a49f'}))
    #print(api.get_api(apiUrls.GET_USERS).json())

    """period = {
        "from": 1684706400,
        "to": 1685916000,
        "periods": {
            0: [10, 11, 12],
            1: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            2: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            3: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            4: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            5: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            6: [8, 9, 10, 11, 12, 13],
            7: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            8: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            9: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            10: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            11: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            12: [8, 9, 10, 11, 12, 13],
            13: [10, 11, 12],
        },
        "accesses": [a['_id'] for a in api.get_api(apiUrls.GET_ACCESSES).json()['accesses']]
    }"""
    
    #print(period)
    #print(api.post_api(apiUrls.POST_PERIOD, payload=period).json())
    #print(api.delete_api(apiUrls.DELETE_PERIOD, path_payload={'id': "646c8c1ccb7f866b56ae6d50"}))
