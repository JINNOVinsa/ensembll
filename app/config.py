# config.py
import os
from dotenv import load_dotenv
from datetime import datetime
from models.api.apiInterface import APIinterface
from models.api.statsApi import StatsInterface
from models.api import statsUrls, apiUrls
from models.database.db_utils import DbInputStream

class Config:
    # Charger les variables d'environnement depuis un fichier .env
    load_dotenv()

    # Configuration de la base de données
    DB_APP = DbInputStream(
        'mysql-app', 
        int(os.getenv("DB_PORT")), 
        os.getenv("DB_ID"), 
        os.getenv("DB_PSWD")
    )
    DB_FLOW = DbInputStream(
        'mysql-flow', 
        int(os.getenv("DB_PORT")), 
        os.getenv("DB_FLOW_ID"), 
        os.getenv("DB_FLOW_PSWD"), 
        database=os.getenv("DB_FLOW_NAME")
    )

    # Configuration de l'API Mail
    MAIL_HOST = os.getenv("API_MAIL_LOG")
    MAIL_PSWD = os.getenv("API_MAIL_PSWD")

    # Configuration des API
    API_LOG = os.getenv("API_PARKKI_LOG")
    API_TOKEN = os.getenv("API_PARKKI_TOKEN")
    API = APIinterface(API_LOG, API_TOKEN)
    API.read_tokens()
    if API.should_refresh():
        try:
            API.refresh_auth_token()
        except ConnectionRefusedError:
            API.fetch_auth_token(API_LOG, API_TOKEN)

    # Configuration des statistiques
    STATS_LOG = os.getenv("STATS_PARKKI_ID")
    STATS_TOKEN = os.getenv("STATS_PARKKI_TOKEN")
    STATS_API = StatsInterface(STATS_LOG, STATS_TOKEN)
    STATS_API.read_tokens()
    if STATS_API.should_refresh():
        try: 
            print('Refresh stats')
            STATS_API.refresh_auth_token()
        except ConnectionRefusedError:
            print('Fetch new')
            STATS_API.fetch_auth_token(STATS_LOG, STATS_TOKEN)

    # Contract and Area Configuration
    CONTRACT = None
    API_CONTRACTS = API.get_api(apiUrls.GET_CONTRACTS).json()['contracts']
    for c in API_CONTRACTS:
        if c['name'] == 'Humanicité':
            CONTRACT = c
            break

    STATS_CONTRACT = None
    r = STATS_API.get_api(statsUrls.GET_CONTRACTS)
    for c in r.json():
        if c["name"] == "Humanicité":
            STATS_CONTRACT = c
            break

    r = STATS_API.get_api(statsUrls.GET_AREAS, query_payload={'contract_id': STATS_CONTRACT['id']})
    AREAS = r.json()["areas"]
    AREA_ID = None
    for a in AREAS:
        if a['type'] == 'PARKANDFLOW':
            AREA_ID = a['id']

    if AREA_ID is None:
        print("Can't retrieve area id from statistics api")
        exit()

    # Capacité du parking et véhicules présents
    r = STATS_API.post_api(statsUrls.GET_GENERAL_STATS_OF_PARKING, payload={'timestamp': datetime.today().timestamp(), 'areas': [AREA_ID]}).json()
    CAPACITY = r['nb_spots']
    PARKED_CARS = r['parked_cars']['value']
