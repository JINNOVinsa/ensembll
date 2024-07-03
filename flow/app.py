#coding: utf-8

from typing import Optional, List
from dotenv import load_dotenv
from os import getenv

import requests
import dotenv
from os import getenv, environ
from time import time

from flask import Flask, request, make_response
from re import search

from mysql.connector import connect

from datetime import datetime

class DbInputStream:

    def __init__(self, host: str, port: int, user: str, pswd: str, database: str = "EnsembllFlow") -> None:
        self.host = host
        self.port = port
        self.user = user
        self.pswd = pswd
        self.database = database
        print(self.pswd)

    def connectToDb(self):
        return connect(host=self.host, port=self.port,
                                 user=self.user, password=self.pswd, database=self.database)

    def disconnect(self, connection):
        connection.close()

    def getCursor(self, connection):
        return connection.cursor()

    def write(self, query: str) -> None:
        connection = self.connectToDb()
        csr = self.getCursor(connection)
        csr.execute(query)
        connection.commit()
        csr.close()
        self.disconnect(connection)

    def read(self, query: str, params: tuple = None) -> list:
        connection = self.connectToDb()
        csr = self.getCursor(connection)
        if params:
            csr.execute(query, params)
        else:
            csr.execute(query)
        result = csr.fetchall()
        csr.close()
        self.disconnect(connection)
        return result

    def close_conn(self) -> None:
        self.connector.close()

GET_BOOKING_FOR_DATETIME_AND_PLATE = """SELECT * FROM Bookings WHERE plate="{plate}" AND startTS<="{datetime}" AND endTS>="{datetime}" """
BASE_URL = "https://cerberus.parkki.io/v1.0.0"
GET_TOKEN = "/auth/login"
GET_REFRESH_TOKEN = "/auth/request_access_token"
POST_OPEN_ACCESS = "/accesses/{id}/open"

class APIinterface:

    def __init__(self, mail, pswd) -> None:
        self.dotenv_file = dotenv.find_dotenv('../app/.env')

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

        r = requests.post(BASE_URL + GET_TOKEN,
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
        r = requests.get(BASE_URL + GET_REFRESH_TOKEN, headers={"Authorization": "Bearer " + self.refresh_token["token"]})
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
                BASE_URL + url.format(**path_parameters), headers={"Authorization": "Bearer " + self.auth_token["token"]}, params=query_payload)
        else:
            response = requests.get(
                BASE_URL + url, headers={"Authorization": "Bearer " + self.auth_token["token"]}, params=query_payload)
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
                BASE_URL + url.format(**path_payload), headers={"Authorization": "Bearer " + self.auth_token["token"]}, json=payload)
        else:
            r = requests.post(
                BASE_URL + url, headers={"Authorization": "Bearer " + self.auth_token["token"]}, json=payload)
        return r

    def read_tokens(self):
        self.auth_token = {
            'token': getenv("API_USER_TOKEN"),
            'expires_at': getenv("API_USER_TOKEN_EXPIRATION")
        }

        self.refresh_token = {
            'token': getenv("API_USER_REFRESH_TOKEN"),
            'expires_at': getenv("API_USER_REFRESH_TOKEN_EXPIRATION")
        }

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

load_dotenv('../app/.env')
db_flow = DbInputStream('127.0.0.1', int(getenv("DB_PORT")), getenv("DB_FLOW_WRITER_ID"), getenv("DB_FLOW_WRITER_PSWD"), database=getenv("DB_FLOW_NAME"))
db = DbInputStream('127.0.0.1', int(getenv("DB_PORT")), getenv("DB_ID"), getenv("DB_PSWD"), database='Ensembll')
api_log = getenv("API_PARKKI_LOG")
api_token = getenv("API_PARKKI_TOKEN")
api = APIinterface(api_log, api_token)
api.read_tokens()

app = Flask(__name__)

def handleOpening(plate: str, mac: str = ""):
    print(f"Tentative d'ouverture pour la plaque {plate}")

    if mac == "24:0f:9b:73:58:a3":
        user_ids = get_user_ids_for_plate(plate)
        if not user_ids:
            print("Aucun utilisateur associé à cette plaque.")
            try:
                db_flow.write(f"""INSERT INTO FailedPlate (plate, record) VALUES ("{plate}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}") """)
                print("Enregistrement FailedPlate réussi")
            except Exception as e:
                print(f"Enregistrement FailedPlate échoué: {e}")
            return
        
        user_id_with_booking = get_user_with_current_booking(user_ids, plate)
        if not user_id_with_booking:
            print("Aucune réservation en cours trouvée pour cette plaque.")
            return
        
        if is_already_parked(user_id_with_booking):
            print(f"Accès refusé pour {plate}: l'utilisateur {user_id_with_booking} a déjà un véhicule garé.")
            return

        # Open
        r1 = api.post_api(POST_OPEN_ACCESS, path_payload={'id': '63e5027875729c00bf3ec7b9'}, payload={'location': {'lat': 50.6510382372813, 'lng': 2.96874134678398}})

        if r1.status_code == 204:
            print(f'Ouverture de la barrière d\'entrée réussie pour {plate}')
            try:
                db_flow.write(f"""INSERT INTO FlowIn (plate, record, userId) VALUES ("{plate}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}", "{user_id_with_booking}") """)
                print("Enregistrement FlowIn réussi")
            except Exception as e:
                print(f"Enregistrement FlowIn échoué: {e}")
        else:
            print(f'Ouverture de la barrière d\'entrée échouée pour {plate}')

    else:
        print(f'Ouverture de la barrière de sortie réussie pour {plate}')
        try:
            db_flow.write(f"""INSERT INTO FlowOut (plate, record) VALUES ("{plate}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}") """)
            print("Enregistrement FlowOut réussi")
        except Exception as e:
            print(f"Enregistrement FlowOut échoué: {e}")

def format_plate(plate: str) -> str:
    if search("[0-9]{4}[A-Z]{2}[0-9]{2}", plate):
        return f"{plate[:4]}-{plate[4:6]}-{plate[6:]}"
    elif search("[0-9]{1}[A-Z]{3}[0-9]{3}", plate):
        return f"{plate[:1]}-{plate[1:4]}-{plate[4:]}"
    elif search("[0-9]{3}[A-Z]{3}[0-9]{2}", plate):
        return f"{plate[:3]}-{plate[3:6]}-{plate[6:]}"
    elif search("[A-Z]{2}[0-9]{3}[A-Z]{2}", plate):
        return f"{plate[:2]}-{plate[2:5]}-{plate[5:]}"

def get_user_with_current_booking(user_ids: List[str], plate: str) -> Optional[str]:
    try:
        user_ids_str = ', '.join(f"'{id}'" for id in user_ids)
        now = datetime.now()
        
        query = f"""
        SELECT usrId, startTS, endTS, repeatInterval, customInterval, customAmount, onMonday, onTuesday, onWednesday, onThursday, onFriday, onSaturday, onSunday, ending
        FROM Bookings
        WHERE usrId IN ({user_ids_str}) AND plate=%s AND ending >= %s
        """
        result = db.read(query, (plate, now))

        for row in result:
            usrId, startTS, endTS, repeatInterval, customInterval, customAmount, onMonday, onTuesday, onWednesday, onThursday, onFriday, onSaturday, onSunday, ending = row
            
            start_time = startTS
            end_time = endTS
            ending_time = ending

            if repeatInterval == 'unique':
                if start_time <= now <= end_time:
                    return usrId

            elif repeatInterval == 'daily':
                if start_time.time() <= now.time() <= end_time.time() and start_time.date() <= now.date() <= ending_time.date():
                    return usrId

            elif repeatInterval == 'weekly':
                if start_time.time() <= now.time() <= end_time.time() and start_time.date() <= now.date() <= ending_time.date() and start_time.weekday() == now.weekday():
                    return usrId

            elif repeatInterval == 'monthly':
                if start_time.time() <= now.time() <= end_time.time() and start_time.day == now.day and start_time.date() <= now.date() <= ending_time.date():
                    return usrId

            elif repeatInterval == 'custom':
                day_checks = {
                    0: onMonday,
                    1: onTuesday,
                    2: onWednesday,
                    3: onThursday,
                    4: onFriday,
                    5: onSaturday,
                    6: onSunday
                }
                if customInterval == 'week':
                    if day_checks[now.weekday()] and start_time.time() <= now.time() <= end_time.time():
                        delta_weeks = (now - start_time).days // 7
                        if delta_weeks % customAmount == 0:
                            return usrId
                elif customInterval == 'day':
                    if start_time.time() <= now.time() <= end_time.time():
                        delta_days = (now - start_time).days
                        if delta_days % customAmount == 0:
                            return usrId
                elif customInterval == 'month':
                    if start_time.time() <= now.time() <= end_time.time():
                        delta_months = (now.year - start_time.year) * 12 + (now.month - start_time.month)
                        if delta_months % customAmount == 0 and start_time.day == now.day:
                            return usrId

        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la réservation pour la plaque {plate}: {e}")
        return None

def is_already_parked(user_ids: List[str]) -> bool:
    try:
        if not user_ids:
            return False
        user_ids_str = ', '.join(f"'{id}'" for id in user_ids)
        query = f"""
        SELECT COUNT(*) FROM FlowIn fi
        LEFT JOIN FlowOut fo ON fi.plate = fo.plate
        WHERE fi.userId IN ({user_ids_str}) AND fo.plate IS NULL
        """
        res = db_flow.read(query)
        if res and res[0]:  # Ensure res is not None and not empty
            return res[0][0] > 0  # Assuming COUNT(*) returns an integer in the first column of the first row
        return False
    except Exception as e:
        print(f"Erreur lors de la récupération des données FlowIn/FlowOut: {e}")
        return False

def get_user_ids_for_plate(plate: str) -> List[str]:
    try:
        query = "SELECT usrId FROM Plates WHERE plate = %s"
        result = db.read(query, (plate,))
        return [row[0] for row in result]
    except Exception as e:
        print(f"Erreur lors de la récupération des ID utilisateurs pour la plaque {plate}: {e}")
        return []

@app.route("/plate", methods=['POST'])
def retrieve_plate():
    payload = request.get_data().decode()
    mac = search(".*<macAddress>(.*)</macAddress>.*", payload).group(1)
    plate = search(".*<licensePlate>([0-9]{4}[A-Z]{2}[0-9]{2}|[0-9]{1}[A-Z]{3}[0-9]{3}|[0-9]{3}[A-Z]{3}[0-9]{2}|[A-Z]{2}[0-9]{3}[A-Z]{2})</licensePlate>.*", payload)

    print(f"Read plate: {plate}")
    print(f"Read mac: {mac}")
    
    if plate is not None:
        plate = plate.group(1)
        formatted_plate = format_plate(plate)

        handleOpening(formatted_plate, mac=mac)
    else:
        print(f"Read plate is invalid ({plate})")

    return make_response("OK", 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
