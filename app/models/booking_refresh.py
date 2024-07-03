from dotenv import load_dotenv
from os import getenv
from time import sleep

from utils import Book
from database.db_utils import DbInputStream
from api.apiInterface import APIinterface
from api import apiUrls

load_dotenv()

db = DbInputStream('127.0.0.1', int(getenv("DB_PORT")), getenv("DB_ID"), getenv("DB_PSWD"))

api_log = getenv("API_PARKKI_LOG")
api_token = getenv("API_PARKKI_TOKEN")

api = APIinterface(api_log, api_token)
api.read_tokens()
if api.should_refresh():
    try:
        api.refresh_auth_token()
    except ConnectionRefusedError:
        api.fetch_auth_token(api_log, api_token)

contracts = api.get_api(apiUrls.GET_CONTRACTS).json()['contracts']
for c in contracts:
    if c['name'] == 'Humanicité':
        api.contract = c
        break

TWELVE_HOURS_IN_SECONDS = 12*60*60
while True:
	Book.refresh_bookings(api, db)
	sleep(TWELVE_HOURS_IN_SECONDS)
print("ok")
