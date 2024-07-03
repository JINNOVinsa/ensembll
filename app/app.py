# coding: utf-8

from static.assets.usr import profilesTypes as img

from models.api.apiInterface import APIinterface
from models.api.statsApi import StatsInterface
from models.api import apiUrls
from models.api import statsUrls
from models.utils import Auth, Book
from models.mailling.mailInterface import Mailling
import models.mailling.mailPayloads as mails
from models.database.db_utils import DbInputStream
import models.database.queries as db_requests
import re

from flask import Flask, render_template, request, make_response, url_for, redirect, jsonify
from datetime import datetime, timedelta, date
import calendar
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

from mysql.connector.errors import IntegrityError

from dotenv import load_dotenv
from os import getenv

from re import match

from uuid import uuid4

# For exporting users
from io import StringIO
import csv


BASE_APP_URL = "https://cogestion-parking.ensembll.fr"

imagePath = "static/assets/park7_logo.png"

app = Flask(__name__)

load_dotenv()
db = DbInputStream('127.0.0.1', int(getenv("DB_PORT")), getenv("DB_ID"), getenv("DB_PSWD"))
db_flow = DbInputStream('127.0.0.1', int(getenv("DB_PORT")), getenv("DB_FLOW_ID"), getenv("DB_FLOW_PSWD"), database=getenv("DB_FLOW_NAME"))

mail_host = getenv("API_MAIL_LOG")
mail_pswd = getenv("API_MAIL_PSWD")

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

stats_log = getenv("STATS_PARKKI_ID")
stats_token = getenv("STATS_PARKKI_TOKEN")

statsApi = StatsInterface(stats_log, stats_token)
statsApi.read_tokens()
statsApi.fetch_auth_token(stats_log, stats_token)
if statsApi.should_refresh():
    try:
        print('Refresh stats')
        statsApi.refresh_auth_token()
    except ConnectionRefusedError:
        print('Fetch new')
        statsApi.fetch_auth_token(stats_log, stats_token)

contract = None

r = statsApi.get_api(statsUrls.GET_CONTRACTS)
for c in r.json():
    if c["name"] == "Humanicité":
        contract = c
        break

r = statsApi.get_api(statsUrls.GET_AREAS, query_payload={'contract_id': contract['id']})
areas = r.json()["areas"]
area_id = None
for a in areas:
    if a['type'] == 'PARKANDFLOW':
        area_id = a['id']

if area_id is None:
    print("Can't retreive area id from statistics api")
    exit()

# Capacité du parking et véhicules présents
r = statsApi.post_api(statsUrls.GET_GENERAL_STATS_OF_PARKING, payload={'timestamp': datetime.today().timestamp(), 'areas': [area_id]}).json()
capacity = r['nb_spots']
parked_cars = r['parked_cars']['value']

@app.route('/', methods=['GET'])
def home():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)
    if usr_id is None:
        return redirect(url_for('login'))

    # Retreive User info
    user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=usr_id))[0]

    # Get user bookings
    usr_bookings = db.read(db_requests.GET_USER_BOOKINGS.format(usrId=usr_id))

    bookings = list()
    for b in usr_bookings:
        startL = list(str(b[4].strftime("%d %B %Y %H:%M")))
        startL[3] = chr(ord(startL[3])-32)

        endL = list(str(b[5].strftime("%d %B %Y %H:%M")))
        endL[3] = chr(ord(endL[3])-32)
        
        book = {
            "id": b[0],
            "immat": b[2],
            "criticity": b[17],
            "book_start": ''.join(startL),
            "book_end": ''.join(endL),
            "duration": str(b[5] - b[4])[:-3].replace("days", "jours").replace("day", "jour").replace(':', 'h ')+"min(s)"
        }
        
        bookings.append(book)
    bookings.sort(key=lambda b: datetime.strptime(
        b["book_start"], '%d %B %Y %H:%M'))
    
    try:
        userRGPD = db.read(db_requests.GET_USER_RGPD.format(usrId=usr_id))[0][0]
    except IndexError:
        userRGPD = 0

    if user[6] == 1:
        entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)
        return render_template('admin-dashboard.html', connected=True, usrFirstname=user[0], checkRGPD=userRGPD, bookings=bookings, adminHeadline="Direction", adminRoute="adminPannel", entities=entities)
    elif user[6] == 2:
        entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)
        return render_template('admin-dashboard.html', connected=True, usrFirstname=user[0], checkRGPD=userRGPD, bookings=bookings, adminHeadline="Administration", adminRoute="superAdminPannel", entities=entities)
    else:
        return render_template('user-dashboard.html', connected=True, usrFirstname=user[0], checkRGPD=userRGPD, bookings=bookings)
    
@app.route('/update-rgpd-consent', methods=['POST'])
def update_rgpd_consent():
    auth_token = request.cookies.get('SESSID', default=None)

    data = request.get_json()
    rgpd_accepted = data['rgpdAccepted']
    user_id = Auth.is_auth(auth_token, db)

    if user_id is None:
        return make_response('UNAUTHORIZED', 401)
    
    if rgpd_accepted is None:
        return make_response('BAD REQUEST', 400)
    
    if rgpd_accepted == 1:
        db.write(db_requests.INSERT_USER_RGPD_TRUE_CONSENT.format(check=1, userID=user_id, date=datetime.now()))
        username = db.read(db_requests.GET_USERNAME_BY_ID.format(id=user_id))[0][0]
        mail = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=user_id))[0][2]
        mailInterface = Mailling(mail_host, mail_pswd)
        try:
            mailInterface.connect()

            mail_text = mailInterface.buildmail(
                mail,
                mails.CONFIRM_CREATE_ACCOUNT['subject'], 
                mails.CONFIRM_CREATE_ACCOUNT['content'].format(username=username),
                imagePath)

            try :
                mailInterface.sendmail(mail, mail_text)
                return make_response("OK", 200)
            except Exception as e:
                print(e)
                return make_response("INTERNAL ERROR", 500)
        except Exception as e:
            print(e)
            return make_response("NETWORK ERROR", 500)
    return make_response('BAD REQUEST', 400)

@app.route('/adminPannel', methods=['GET'])
def adminPannel():
    return redirect(url_for('adminPannelUsers'))

@app.route('/adminPannel/users', methods=['GET'])
def adminPannelUsers():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_admin(usr_id, db):
        return make_response("UNAUTHORIZED", 401)

    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_id))[0][0]
    count = db.read(db_requests.GET_USERS_COUNT_BY_ENTITY.format(entityId=admin_entity))[0][0]

    pNames = [p[0] for p in db.read(db_requests.GET_PROFILES_NAMES_BY_ENTITY.format(entityId=admin_entity))]
    return render_template("admin-pannel-users.html", connected=True, usercount=count, profilesNames=pNames)

@app.route('/adminPannel/confirm', methods=['GET'])
def adminPannelConfirm():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)
    
    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_admin(usr_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    entity_id = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_id))[0][0]
    users_count = db.read(db_requests.GET_USERS_TO_CONFIRM_COUNT_BY_ENTITY_COUNT.format(entityId=entity_id))[0][0]

    pNames = [p[0] for p in db.read(db_requests.GET_PROFILES_NAMES)]
    return render_template("admin-pannel-confirm.html", connected=True, usercount=users_count, profilesNames=pNames)

@app.route('/superAdminPannel/profiles', methods=['GET'])
def superAdminPannelProfiles():
    auth_token = request.cookies.get('SESSID', default=None)
    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_super_admin(usr_id, db):
        return make_response("UNAUTHORIZED", 401)

    # Récupération de toutes les entités
    entities = db.read(db_requests.GET_ALL_ENTITIES)

    # Récupération de tous les profils
    all_profiles = db.read(db_requests.GET_PROFILES)

    # Organiser les profils par entité
    profiles_by_entity = {}
    for entity in entities:
        entity_id = entity[0]  # ID de l'entité
        entity_profiles = [p for p in all_profiles if p[3] == entity_id]  # Comparaison de l'entityId du profil
        profiles_by_entity[entity_id] = {
            "entity": {"id": entity_id, "eName": entity[1]},
            "profiles": entity_profiles,
            "can_add": len(entity_profiles) < 5
        }

    userHierarchy = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=usr_id))[0]

    return render_template("super-admin-pannel-profiles.html", connected=True, profiles_by_entity=profiles_by_entity, userHierarchy=userHierarchy[6], entities=entities)


@app.route('/superAdminPannel/timeslots', methods=['GET'])
def superAdminPannelProfilfesTimeSlots():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    profile_id = request.args.get("profile", default=None)

    if profile_id is None:
        return make_response("BAD REQUEST", 400)
    
    time_slots = db.read(db_requests.GET_PROFILE_TIME_SLOTS.format(profileId=profile_id))
    time_slots.sort(key=lambda t: t[4], reverse=True)
    
    time_slots_list = list()
    for t in time_slots:
        time_slots_list.append({
            "id": t[0],
            "profileId": t[1],
            "start": str(t[2]),
            "end": str(t[3]),
            "level": t[4]
        })

    return make_response(time_slots_list, 200)

@app.route('/superAdminPannel/addtimeslots', methods=['POST'])
def superAdminPannelAddTimeSlot():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    profile = request.form.get("profile", default=None)
    if profile is None:
        return make_response("BAD REQUEST", 400)
    
    entity_id = db.read(db_requests.GET_ENTITY_FROM_PROFILE.format(id=profile))
    if entity_id is None:
        return make_response("BAD REQUEST", 400)
    
    is_profile_exists = db.read(db_requests.EXISTS_PROFILE_BY_ID_AND_ENTITY.format(profileId=profile, entityId=entity_id[0][0]))

    if is_profile_exists[0][0] == 0:
        return make_response("NOT FOUND", 404)


    start = request.form.get("start", default=None)
    end = request.form.get("end", default=None)
    level = request.form.get("level", default=None)

    if start is None or end is None or level is None:
        return make_response("BAD REQUEST", 400)
    
    if not match('^(0|1|2)[0-9]:[0-6][0-9]:00', start) or not match('^(0|1|2)[0-9]:[0-6][0-9]:00', end) or not level.isdigit():
        return make_response("BAD REQUEST", 400)

    db.write(db_requests.INSERT_PROFILE_TIME_SLOTS.format(profileId=profile, start=start, end=end, level=level))
    return make_response("CREATED", 201)

@app.route('/superAdminPannel/deletetimeslot', methods=['POST'])
def superAdminPannelDeleteTimeSlot():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    time_slot_id = request.form.get("timeslot", default=None)

    if time_slot_id is None:
        return make_response("BAD REQUEST", 400)
 
    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]
    time_slot = db.read(db_requests.GET_TIME_SLOT_BY_ID.format(id=time_slot_id))

    try:
        time_slot = time_slot[0]
    except:
        return make_response("NOT FOUND", 404)
    
    db.write(db_requests.DELETE_TIME_SLOT.format(id=time_slot_id))

    return make_response("OK", 200)

@app.route('/getUserInformation', methods=['GET'])
def getUserInformation():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)
    if usr_id is None:
        return make_response('UNAUTHORIZED', 401)

    user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=usr_id))[0]
    user_plates = db.read(db_requests.GET_USER_PLATES.format(usrId=usr_id))

    user_payload = {
        "firstName": user[0],
        "lastName": user[1],
        "email": user[2],
        "plates": [p[0] for p in user_plates]
    }

    return make_response(jsonify(user_payload), 200)

@app.route('/report/other', methods=['POST'])
def reportOther():
    auth_token = request.cookies.get('SESSID', default=None)
    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    comment = request.form.get('comment')

    mailInterface = Mailling(mail_host, mail_pswd)
    try:
        mailInterface.connect()

        mail_text = mailInterface.buildmail(
            mail_host,
            mails.REPORT_PROBLEM["subject"],
            mails.REPORT_PROBLEM["content"].format(firstName=firstName, lastName=lastName, email=email, comment=comment),
            imagePath)

        mailInterface.sendmail(mail_host, mail_text)
        return make_response("OK", 200)
    except Exception as e:
        print(e)
        return make_response("NETWORK ERROR", 500)
    

@app.route('/report/bearer', methods=['POST'])
def reportBearer():
    plate = request.form.get('plateNumber')
    lastName = request.form.get('lastName')
    firstName = request.form.get('firstName')
    email = request.form.get('email')
    passageDateTime = request.form.get('passageDate') + ' ' + request.form.get('passageTime')
    
    # Conversion de la chaîne de caractères en objet datetime
    try:
        passageDateTime = datetime.strptime(passageDateTime, '%Y-%m-%d %H:%M')
    except ValueError:
        return make_response("BAD REQUEST - Invalid Date Format", 400)
    
    # Calcul des intervalles de temps
    startTime = passageDateTime - timedelta(minutes=15)
    endTime = passageDateTime + timedelta(minutes=15)

    # Requête pour récupérer les plaques dans l'intervalle de temps
    flowInPlates = db_flow.read(db_requests.GET_PLATE_IN_RECORDS.format(startTS=startTime, endTS=endTime))
    print(flowInPlates)
    
    plateFound = False
    if len(flowInPlates) != 0:
        # Vérification si la plaque existe dans les résultats
        plateFound = any(plate == record[0] for record in flowInPlates)

    errorId = ""
    if plateFound:
        errorId = "bearerFalse"

    if errorId and errorId != "bearerTrue":
        flowInPlatesError = db_flow.read(db_requests.GET_PLATE_IN_RECORDS_ERRORS.format(startTS=startTime, endTS=endTime))
        # Vérification des erreurs de lecture
        for record in flowInPlatesError:
            similarity = plates_are_similar(plate, record[0])
            if similarity:
                errorId = "bearerTrue"
                db.write(db_requests.INSERT_READING_PLATE.format(theoricalPlate=plate, readingPlate=record[0], trueLetter=similarity[0], falseLetter=similarity[1]))

                mailerInterface = Mailling(mail_host, mail_pswd)
                try:
                    mailerInterface.connect()
                    mail_text = mailerInterface.buildmail(
                        mail_host,
                        mails.REPORT_PLATE["subject"],
                        mails.REPORT_PLATE["content"].format(lastName=lastName, firstName=firstName, email=email, theoreticalPlate=plate, realPlate=record[0], X=similarity[0], Y=similarity[1]),
                        imagePath)
                    mailerInterface.sendmail(mail_host, mail_text)
                    break
                except Exception as e:
                    print(e)
                    return make_response("NETWORK ERROR", 500)
    
    # Mise à jour de la table des erreurs
    if errorId and (errorId == "bearerTrue" or errorId == "bearerFalse"):
        try:
            db.write(db_requests.UPDATE_ERRORS.format(id=errorId))
            return make_response(jsonify({"message": "Report processed successfully"}), 200)
        except Exception as e:
            return make_response("DATABASE ERROR", 500)
    else:
        return make_response("OK", 200)
    
def plates_are_similar(plate1, plate2):
    # Convertit les deux plaques en un format uniforme en enlevant les tirets pour la comparaison
    formatted_plate1 = plate1.replace('-', '')
    formatted_plate2 = plate2.replace('-', '')

    # La longueur des plaques doit être égale pour être comparées
    if len(formatted_plate1) != len(formatted_plate2):
        return False

    # Comparer les plaques caractère par caractère
    differences = [(a, b) for a, b in zip(formatted_plate1, formatted_plate2) if a != b]

    # S'il y a exactement une différence, cela pourrait indiquer une erreur de lecture
    if len(differences) == 1:
        # Retourne le tuple de la différence pour une utilisation ultérieure
        return differences[0]
    
    return False
    
@app.route('/get_error_counts', methods=['GET'])
def get_error_counts():
    try:
        bearerTrue_count = db.read("SELECT value FROM Errors WHERE id = 'bearerTrue'")[0][0]
        bearerFalse_count = db.read("SELECT value FROM Errors WHERE id = 'bearerFalse'")[0][0]
        return jsonify(bearerTrue=bearerTrue_count, bearerFalse=bearerFalse_count)
    except Exception as e:
        print(e)
        return make_response("DATABASE ERROR", 500)
    
@app.route('/report/planningFull', methods=['POST'])
def reportPlanningFull():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)
    if usr_id is None:
        return redirect(url_for('login'))

    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')

    bookingStartDate = request.form.get('bookingStartDate')
    bookingStartTime = request.form.get('bookingStartTime')
    bookingEndDate = request.form.get('bookingEndDate')
    bookingEndTime = request.form.get('bookingEndTime')
    repetition = request.form.get('repetition')

    if repetition == "none" :
        repetition = "Pas de répétition"
    elif repetition == "daily" :
        repetition = "Quotidienne"
    elif repetition == "weekly" :
        repetition = "Hebdomadaire"
    elif repetition == "monthly" :
        repetition = "Mensuelle"
    elif repetition == "custom" :
        repetition = "Personnalisé"

    mailInterface = Mailling(mail_host, mail_pswd)
    try:
        mailInterface.connect()

        mail_text = mailInterface.buildmail(
            mail_host,
            mails.REPORT_PLANNING_FULL["subject"],
            mails.REPORT_PLANNING_FULL["content"].format(firstName=firstName, lastName=lastName, email=email, bookingStartDate=bookingStartDate, bookingStartTime=bookingStartTime, bookingEndDate=bookingEndDate, bookingEndTime=bookingEndTime, repetition=repetition),
            imagePath)

        mailInterface.sendmail(mail_host, mail_text)
        return make_response("OK", 200)
    except Exception as e:
        print(e)
        return make_response("NETWORK ERROR", 500)

@app.route('/adminPannel/bookings', methods=['GET'])
def adminPannelBookings():

    auth_token = request.cookies.get("SESSID", default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'), 302)
    
    if not Auth.is_admin(usr_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    # Get admin entity
    try:
        eId = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_id))[0][0]
        bCount = db.read(db_requests.GET_CURRENT_USERS_BOOKINGS_COUNT_FROM_ENTITY_ID.format(entityId=eId))[0][0]
    except IndexError:
        return make_response("BAD REQUEST", 400)

    return render_template('admin-pannel-bookings.html', connected=True, bookingcount=bCount)

@app.route('/adminPannel/fetchUserPlates', methods=['GET'])
def adminPannelUserPlates():
    auth_token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)
    
    user_id = request.args.get('usrID', default=None)

    if user_id is None:
        return make_response('BAD REQUEST', 400)
    
    # Verify admin is in user entity
    user_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=user_id))[0][0]
    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]

    if user_entity != admin_entity:
        return make_response('UNAUTHORIZED', 401)

    plates = db.read(db_requests.GET_USER_PLATES.format(usrId=user_id))
    return make_response(plates, 200)

@app.route('/superAdminPannel', methods=['GET'])
def superAdminPannel():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_super_admin(usr_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    return redirect(url_for('superAdminPannelUsers'))

@app.route('/superAdminPannel/users', methods=['GET'])
def superAdminPannelUsers():
    # Here we retreive all users independant from entities

    token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(token, db)
    
    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)
    
    users_count = db.read(db_requests.GET_USERS_AND_ADMIN_COUNT)[0][0]
    entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)
    profiles = db.read(db_requests.GET_PROFILES)

    return render_template('super-admin-pannel-users.html', connected=True, usercount=users_count, entities=entities, profiles=profiles)

@app.route('/get_profiles_by_entity', methods=['GET'])
def get_profiles_by_entity():
    entity_id = request.args.get('entityId')
    profiles = db.read(db_requests.GET_PROFILES_BY_ENTITY.format(entityId=entity_id))
    return jsonify(profiles)

@app.route('/superAdminPannel/confirm', methods=['GET'])
def superAdminPannelConfirm():
    token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))

    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)

    user_count = db.read(db_requests.GET_USERS_TO_CONFIRM_COUNT)[0][0]
    pNames = [p[0] for p in db.read(db_requests.GET_PROFILES_NAMES)]
    entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)

    return render_template('super-admin-pannel-confirm.html', connected=True, usercount=user_count, profilesNames=pNames, entities=entities)

@app.route('/superAdminPannel/allocation', methods=['GET'])
def superAdminPannelAllocation():
    token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 400)
    
    es = db.read(db_requests.GET_ALL_ENTITIES)
    
    entities = list()
    parked_cars = 0
    for e in es:
        entities.append({
            'id': e[0],
            'name': e[1],
            'allocated': e[2],
            'free': "##" #CALL API #e[2] - db.read(db_requests.GET_ENTITY_FREE_SPOTS.format(entityId=e[0]))[0][0]
        })
        parked_cars = parked_cars + e[2]

    stat = statsApi.post_api(statsUrls.GET_GENERAL_STATS_OF_PARKING, payload={'timestamp': datetime.now().timestamp(), 'areas': [area_id]})
    
    if stat.status_code == 200:
        spots = stat.json()['nb_spots']
    else:
        spots = '###'

    nbFreePlaces = spots - parked_cars
    userHierarchy = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=admin_id))[0]

    return render_template('super-admin-pannel-allocation.html', connected=True, total_spots=spots, entry=entities, nbFreePlaces=nbFreePlaces, userHierarchy=userHierarchy)

@app.route('/superAdminPannel/bookings', methods=['GET'])
def superAdminPannelBookings():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 400)
    
    bookings_count = db.read(db_requests.GET_CURRENT_BOOKINGS_COUNT)[0][0]

    return render_template('super-admin-pannel-bookings.html', connected=True, bookingcount=bookings_count)

@app.route('/adminPannel/getUser', methods=['GET'])
def getUser():
    auth_token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    if (request.args.get('usrID') == None):
        return make_response("BAD REQUEST", 400)

    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]

    usr_db = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=str(request.args.get('usrID'))))[0]

    if usr_db[7] != admin_entity:
        # An admin tries to fetch an user which is not in his entity
        return make_response("UNAUTHORIZED", 401)

    profile_name = db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=str(usr_db[4])))
    plates = db.read(db_requests.GET_USER_PLATES.format(usrId=str(request.args.get('usrID'))))

    usr_payload = {
        "firstname": usr_db[0],
        "lastname": usr_db[1],
        "mail": usr_db[2],
        "tel": usr_db[3],
        "profile": profile_name,
        "criticity": 0,
        "plates": [p[0] for p in plates]
    }

    return make_response(jsonify(usr_payload), 200)

@app.route('/adminPannel/getAllUsers', methods=['GET'])
def getAllUsersFromEntity():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]

    users = db.read(db_requests.GET_USERS_FROM_ENTITY.format(entityId=admin_entity))
    users_list = list()
    for u in users:
        plates = [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=u[0]))]
        try:
            db.read(db_requests.GET_USER_RGPD.format(usrId=u[0]))[0][0]
            userRGPD = "Oui"
        except:
            userRGPD = "Non"
        users_list.append({
            'id': u[0],
            'firstName': u[1],
            'lastName': u[2],
            'mail': u[3],
            'phoneNumber': u[4],
            'profile': db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=u[5]))[0][0],
            "criticity": 0,
            'hierarchy': u[7],
            'entity': u[9],
            'approbation': u[6],
            'plates': plates,
            'rgpd': userRGPD
        })

    return make_response(users_list, 200)

@app.route('/adminPannel/getAllBookings', methods=['GET'])
def getAllBookingsFromEntity():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]

    # Fetch bookings for admin's entity
    dbBookings = db.read(db_requests.GET_CURRENT_BOOKING_FROM_ENTITY_ID.format(entityId=admin_entity))
    
    entityBookings = list()
    for b in dbBookings:
        startB = list(str(b[4].strftime("%d %B %Y %H:%M")))
        startB[3] = chr(ord(startB[3])-32)

        endB = list(str(b[5].strftime("%d %B %Y %H:%M")))
        endB[3] = chr(ord(endB[3])-32)

        endingB = list(str(b[16].strftime("%d %B %Y %H:%M")))
        endingB[3] = chr(ord(endingB[3])-32)
        entityBookings.append({
            'bookingID': b[0],
            'bookingPlate': b[2],
            'bookingPresent': b[3],
            'bookingStart': b[4],
            'bookingEnd': b[5],
            'bookingDuration': str(b[5] - b[4])[:-3].replace("days", "jours").replace("day", "jour").replace(':', 'h ')+"min(s)",
            'bookingRepeat': b[6],
            'bookingRepeatCustomInterval': b[7],
            'bookingRepeatCustomAmount': b[8],
            'bookingRepeatCustomMonday': b[9],
            'bookingRepeatCustomTuesday': b[10],
            'bookingRepeatCustomWednesday': b[11],
            'bookingRepeatCustomThursday': b[12],
            'bookingRepeatCustomFriday': b[13],
            'bookingRepeatCustomSaturday': b[14],
            'bookingRepeatCustomSunday': b[15],
            'bookingRepeatEnding': b[16],
            'criticity': b[17],
            'userId': b[18],
            'userFirstname': b[19],
            'userLastname': b[20],
            'userMail': b[21],
            'userPhoneNumber': b[22],
            'userProfile': db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=b[23]))[0][0]
        })

    return make_response(jsonify(entityBookings), 200)

@app.route('/adminPannel/confirmUser', methods=['POST'])
def confirmUser():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)

    to_confirm_user = str(request.form.get('USR_ID'))

    try:
        db.write(db_requests.CONFIRM_USER.format(usrId=to_confirm_user))
        mailInterface = Mailling(mail_host, mail_pswd)
        mail = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=to_confirm_user))[0][2]

        try:
            mailInterface.connect()

            mail_text = mailInterface.buildmail(
                mail,
                mails.CONFIRM_UPDATE_ACCOUNT["subject"],
                mails.CONFIRM_UPDATE_ACCOUNT["content"],
                imagePath)
            mailInterface.sendmail(mail, mail_text)
            return make_response("OK", 200)
        except Exception as e:
            print(e)
            return make_response("NETWORK ERROR", 500)
    except Exception as e:
        return make_response('BAD REQUEST', 400)
    return make_response('OK', 200)

@app.route('/adminPannel/editUser', methods=['PUT'])
def editUser():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    usrId = request.form.get("id")
    usrEntity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usrId))[0][0]

    # Check if user is in the same entity as the admin -(never trust client side data)-
    try:
        if db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0] != usrEntity:
            return make_response("UNAUTHORIZED", 401)
    except:
        return make_response("BAD REQUEST", 400)

    lastname = str(request.form.get("lastname"))
    firstname = str(request.form.get("firstname"))
    mail = str(request.form.get("mail"))
    tel = str(request.form.get("tel"))
    profile = str(request.form.get("profile"))
    
    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", tel):
        return make_response("INVALID TEL", 400)
    
    if not match("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", mail):
        return make_response("INVALID MAIL", 400)
    
    pId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(name=profile))

    if len(pId) <= 0:
        return make_response("INVALID PROFILE", 400)

    try:
        db.write(db_requests.UPDATE_USER_WITH_TEL_BY_ID.format(lname=lastname, fname=firstname, mail=mail, tel=tel, entityId=usrEntity, pId=pId[0][0], usrId=usrId))
        api.put_api(apiUrls.PUT_USER, path_payload={'id': usrId}, data_payload={
            "firstname": firstname,
            "lastname": lastname,
            "email": mail,
            "contracts": [api.contract["_id"]]
        })
        return make_response("OK", 200)
    except Exception as e:
        return make_response("BAD REQUEST", 400)

@app.route('/adminPannel/deleteUser', methods=['POST'])
def deleteUser():
    auth_token = request.cookies.get("SESSID", default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)

    usr_to_delete = request.form.get('usrId', default=None)

    if usr_to_delete is None:
        return make_response('BAD REQUEST', 400)
    
    if db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_to_delete))[0][0] != db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_id))[0][0]:
        return make_response('UNAUTHORIZED', 401)

    db.write(db_requests.DELETE_USER_PASSWORD_RESET_REQUEST.format(usrId=str(usr_to_delete)))
    db.write(db_requests.DELETE_USER_TOKEN_BY_ID.format(id=str(usr_to_delete)))
    db.write(db_requests.DELETE_USER_CREDENTIALS_BY_ID.format(id=str(usr_to_delete)))
    db.write(db_requests.DELETE_USER_PLATES.format(id=str(usr_to_delete)))
    db.write(db_requests.DELETE_USER_BY_ID.format(id=str(usr_to_delete)))
    db.write(db_requests.DELETE_USER_RGPD_BY_ID.format(usrId=str(usr_to_delete)))

    api.delete_api(apiUrls.DELETE_USER, path_payload={'id': usr_to_delete})
    return make_response('OK', 200)

@app.route('/adminPannel/exportUsers', methods=['GET'])
def adminExportUser():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if admin_id is None:
        return redirect(url_for('login'))

    if not Auth.is_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)

    entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]

    users = db.read(db_requests.GET_USERS_FROM_ENTITY.format(entityId=entity))

    # Create the csv
    data = list()
    for user in users:
        user_plates = db.read(db_requests.GET_USER_PLATES.format(usrId=user[0]))
        first_plate = 'Non renseignée'
        second_plate = 'Non renseignée'
        if len(user_plates) > 0:
            first_plate = user_plates[0][0]
            if len(user_plates) > 1:
                second_plate = user_plates[1][0]

        data.append([
            user[1],        # Firstname
            user[2],        # Lastname
            user[3],        # Mail
            user[4],        # Phone number
            db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=user[5]))[0][0],    # Profile name
            first_plate,     
            second_plate
        ])
    stream = StringIO()
    cw = csv.writer(stream)
    cw.writerow(['Prénom', 'Nom', 'Adresse mail', 'Numéro de téléphone', 'Profil', 'Plaque d\'immatriculation 1', 'Plaque d\'immatriculation 2'])
    cw.writerows(data)

    response = make_response(stream.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=\"users.csv\""
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/adminPannel/addProfile', methods=['POST'])
def addProfile():
    auth_token = request.cookies.get("SESSID", default=None)

    user_id = Auth.is_auth(auth_token, db)

    if user_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(user_id, db):
        return make_response("UNAUTHORIZED", 401)

    profile_entity = str(request.form.get("entity"));
    profile_name = str(request.form.get("name"));
    profile_criticity = request.form.get("criticity");

    try:
        profile_criticity = int(profile_criticity)
    except TypeError:
        return make_response("BAD REQUEST", 400)

    db.write(db_requests.INSERT_PROFILE.format(pName=profile_name, pCriticity=profile_criticity, entityId=profile_entity))

    return make_response("OK", 200)

@app.route('/adminPannel/editProfile', methods=['PUT'])
def editProfile():
    auth_token =request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)
    
    pID = request.form.get('id')
    newName = request.form.get('name')
    newCriticity = request.form.get('criticity')

    try:
        db.write(db_requests.UPDATE_PROFILE_BY_ID.format(newName=newName, newCriticity=newCriticity, pId=pID))
    except Exception as e:
        return make_response("BAD REQUEST", 400)

    return make_response("OK", 200)

@app.route('/adminPannel/deleteProfile', methods=['DELETE'])
def deleteProfile():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    profile_id = request.form.get('profileId', default=None)

    if profile_id is None:
        return make_response("BAD REQUEST", 400)
    
    profile_name = db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=profile_id))
    
    if len(profile_name) == 0 or profile_name[0][0] == 'Aucun Profil':
        return make_response("BAD REQUEST", 400)
    
    # Get profile's id for No profile
    no_profile_id = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(name="Aucun Profil"))[0][0]

    # Change profile's users to No profile
    db.write(db_requests.UPDATE_USERS_PROFILE.format(newProfileId=no_profile_id, oldProfileId=profile_id))

    # Delete profile from db
    db.write(db_requests.DELETE_PROFILE.format(profileId=profile_id))

    return make_response("OK", 200)

@app.route('/superAdminPannel/editAllocation', methods=['PUT'])
def editAllocation():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for("login"))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    entity = request.form.get("id", default=None)
    if entity is None:
        return make_response("BAD REQUEST", 400)
    
    spots = request.form.get("spots", default=None)
    try:
        spots = int(spots)
    except ValueError:
        return make_response("BAD REQUEST", 400)
    
    try:
        db.write(db_requests.UPDATE_ENTITY_SPOTS.format(spots=spots, id=entity))
        return make_response('OK', 200)
    except Exception:
        return make_response('BAD REQUEST', 400)

@app.route('/superAdminPannel/getAllUsersAndAdmin', methods=['GET'])
def getAllUsersAndAdmin():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    try:
        db.read(db_requests.GET_USER_RGPD.format(usrId=admin_id))[0][0]
        userRGPD = True
    except:
        userRGPD = False

    users = db.read(db_requests.GET_USERS_AND_ADMIN)
    users_list = list()
    for u in users:
        plates = [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=u[0]))]
        try:
            db.read(db_requests.GET_USER_RGPD.format(usrId=u[0]))[0][0]
            userRGPD = "Oui"
        except:
            userRGPD = "Non"
        users_list.append({
            'id': u[0],
            'firstName': u[1],
            'lastName': u[2],
            'mail': u[3],
            'phoneNumber': u[4],
            'profile': db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=u[5]))[0][0],
            "criticity": 0,
            'approbation': u[6],
            'hierarchy': u[7],
            'entityId': u[8],
            'entity': u[9],
            'plates': plates,
            'rgpd': userRGPD
        })

    return make_response(users_list, 200)

@app.route('/superAdminPannel/editUser', methods=['PUT'])
def superEditUser():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    usrId = request.form.get("id")

    lastname = str(request.form.get("lastname"))
    firstname = str(request.form.get("firstname"))
    mail = str(request.form.get("mail"))
    tel = str(request.form.get("tel"))
    entity = str(request.form.get("entityId"))
    profile = str(request.form.get("profile"))

    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", tel):
        return make_response("INVALID TEL", 400)
    
    if not match("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", mail):
        return make_response("INVALID MAIL", 400)
    
    pId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(name=profile))

    if len(pId) <= 0:
        return make_response("INVALID PROFILE", 400)

    try:
        db.write(db_requests.UPDATE_USER_WITH_TEL_BY_ID.format(lname=lastname, fname=firstname, mail=mail, tel=tel, entityId=entity, pId=pId[0][0], usrId=usrId))
        api.put_api(apiUrls.PUT_USER, path_payload={'id': usrId}, data_payload={
            "firstname": firstname,
            "lastname": lastname,
            "email": mail,
            "contracts": [api.contract["_id"]]
        })
        return make_response("OK", 200)
    except Exception as e:
        return make_response("BAD REQUEST", 400)

@app.route('/superAdminPannel/confirmUser', methods=['POST'])
def superConfirmUser():
    auth_token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if admin_id is None:
        return redirect(url_for('login'))

    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)

    to_confirm_user = str(request.form.get('USR_ID'))

    try:
        db.write(db_requests.CONFIRM_USER.format(usrId=to_confirm_user))
        mailInterface = Mailling(mail_host, mail_pswd)
        mail = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=to_confirm_user))[0][2]

        try:
            mailInterface.connect()

            mail_text = mailInterface.buildmail(
                mail,
                mails.CONFIRM_UPDATE_ACCOUNT["subject"],
                mails.CONFIRM_UPDATE_ACCOUNT["content"],
                imagePath)
            mailInterface.sendmail(mail, mail_text)
            return make_response("OK", 200)
        except Exception as e:
            print(e)
            return make_response("NETWORK ERROR", 500)
    except Exception as e:
        return make_response('BAD REQUEST', 400)
    return make_response('OK', 200)

@app.route('/superAdminPannel/deleteUser', methods=['POST'])
def superDeleteUser():
    auth_token = request.cookies.get("SESSID", default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)

    usr_to_delete = request.form.get('usrId', default=None)

    if usr_to_delete is None:
        return make_response('BAD REQUEST', 400)
    
    try:
        # Order if very important to avoid delete of certain field before integrity exception
        db.write(db_requests.DELETE_USER_PLATES.format(id=str(usr_to_delete)))
        db.write(db_requests.DELETE_USER_PASSWORD_RESET_REQUEST.format(usrId=str(usr_to_delete)))
        db.write(db_requests.DELETE_USER_TOKEN_BY_ID.format(id=str(usr_to_delete)))
        db.write(db_requests.DELETE_USER_CREDENTIALS_BY_ID.format(id=str(usr_to_delete)))
        db.write(db_requests.DELETE_USER_RGPD_BY_ID.format(usrId=str(usr_to_delete)))
        db.write(db_requests.DELETE_USER_BY_ID.format(id=str(usr_to_delete)))
    except:
        return make_response('BAD REQUEST', 400)
    api.delete_api(apiUrls.DELETE_USER, path_payload={'id': usr_to_delete})
    return make_response('OK', 200)

@app.route('/superAdminPannel/exportUsers', methods=['GET'])
def superAdminExportUsers():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if admin_id is None:
        return redirect(url_for('login'))

    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)

    users = db.read(db_requests.GET_USERS_AND_ADMIN)

    # Create the csv
    data = list()
    for user in users:
        user_plates = db.read(db_requests.GET_USER_PLATES.format(usrId=user[0]))
        first_plate = 'Non renseignée'
        second_plate = 'Non renseignée'
        if len(user_plates) > 0:
            first_plate = user_plates[0][0]
            if len(user_plates) > 1:
                second_plate = user_plates[1][0]

        data.append([
            user[1],        # Firstname
            user[2],        # Lastname
            user[3],        # Mail
            user[4],        # Phone number
            db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=user[5]))[0][0],    # Profile name
            user[9],        # Entity
            first_plate,     
            second_plate
        ])
    stream = StringIO()
    cw = csv.writer(stream)
    cw.writerow(['Prénom', 'Nom', 'Adresse mail', 'Numéro de téléphone', 'Profil', 'Structure', 'Plaque d\'immatriculation 1', 'Plaque d\'immatriculation 2'])
    cw.writerows(data)

    response = make_response(stream.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=\"users.csv\""
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/superAdminPannel/getAllBookings', methods=['GET'])
def superGetAllBookingsFromEntity():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
    # Fetch bookings for admin's entity
    dbBookings = db.read(db_requests.GET_ALL_CURRENT_BOOKINGS)

    entityBookings = list()
    for b in dbBookings:
        startB = list(str(b[4].strftime("%d %B %Y %H:%M")))
        startB[3] = chr(ord(startB[3])-32)

        endB = list(str(b[5].strftime("%d %B %Y %H:%M")))
        endB[3] = chr(ord(endB[3])-32)

        endingB = list(str(b[16].strftime("%d %B %Y %H:%M")))
        endingB[3] = chr(ord(endingB[3])-32)
        entityBookings.append({
            'bookingID': b[0],
            'bookingPlate': b[2],
            'bookingPresent': b[3],
            'bookingStart': b[4],
            'bookingEnd': b[5],
            'bookingDuration': str(b[5] - b[4])[:-3].replace("days", "jours").replace("day", "jour").replace(':', 'h ')+"min(s)",
            'bookingRepeat': b[6],
            'bookingRepeatCustomInterval': b[7],
            'bookingRepeatCustomAmount': b[8],
            'bookingRepeatCustomMonday': b[9],
            'bookingRepeatCustomTuesday': b[10],
            'bookingRepeatCustomWednesday': b[11],
            'bookingRepeatCustomThursday': b[12],
            'bookingRepeatCustomFriday': b[13],
            'bookingRepeatCustomSaturday': b[14],
            'bookingRepeatCustomSunday': b[15],
            'bookingRepeatEnding': b[16],
            'criticity': b[17],
            'userId': b[18],
            'userFirstname': b[19],
            'userLastname': b[20],
            'userMail': b[21],
            'userPhoneNumber': b[22],
            'userProfile': db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=b[23]))[0][0]
        })

    return make_response(jsonify(entityBookings), 200)

@app.route('/superAdminPannel/getAllUsers', methods=['GET'])
def getAllUsers():
    auth_token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    users = db.read(db_requests.GET_USERS_AND_ADMIN)
    users_list = list()
    for u in users:
        plates = [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=u[0]))]
        users_list.append({
            'id': u[0],
            'firstName': u[1],
            'lastName': u[2],
            'mail': u[3],
            'phoneNumber': u[4],
            'profile': db.read(db_requests.GET_PROFILE_NAME_BY_ID.format(id=u[5]))[0][0],
            "criticity": 0,
            'approbation': u[6],
            'plates': plates
        })

    return make_response(users_list, 200)

@app.route('/superAdminPannel/fetchUserPlates', methods=['GET'])
def superAdminPannelUserPlates():
    auth_token = request.cookies.get('SESSID', default=None)

    admin_id = Auth.is_auth(auth_token, db)

    if not Auth.is_super_admin(admin_id, db):
        return make_response('UNAUTHORIZED', 401)
    
    user_id = request.args.get('usrID', default=None)

    if user_id is None:
        return make_response('BAD REQUEST', 400)
    
    plates = db.read(db_requests.GET_USER_PLATES.format(usrId=user_id))
    return make_response(plates, 200)

@app.route('/login', methods=["GET"])
def login():
    return render_template('login.html', connected=False, error=False)

@app.route('/login', methods=['POST'])
def submitLogin():
    req_data = dict(request.form)

    usrCredentials = db.read(
        db_requests.GET_USER_CREDENTIALS.format(login=req_data["login"]))

    if len(usrCredentials) <= 0:
        return render_template('login.html', error=True)

    elif Auth.check_password(req_data['pswd'], usrCredentials[0][0], usrCredentials[0][1]):
        usrID = db.read(db_requests.GET_USER_ID_BY_LOGIN.format(
            login=req_data["login"]))[0][0]

        db.write(db_requests.DELETE_USER_TOKEN_BY_ID.format(id=usrID))

        auth_token = uuid4().hex

        db.write(db_requests.INSERT_USER_TOKEN.format(
            token=auth_token, usrId=usrID))

        resp = make_response(redirect(url_for('home')), 302)
        resp.set_cookie('SESSID', auth_token, path='/')
        return resp

    else:
        return render_template('login.html', connected=False, error=True)

@app.route('/logout')
def logout():
    token = request.cookies.get('SESSID', default=None)
    # Delete auth token
    if token != None:
        db.write(db_requests.DELETE_USER_TOKEN_BY_TOKEN.format(token=token))

    return redirect(url_for('home'))

@app.route('/newaccount', methods=['GET'])
def create_account():
    entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)

    return render_template('new-account.html', connected=False, mailAlreadyBound=False, entities=entities)

@app.route('/newaccount', methods=['POST'])
def submitAccount():
    # Check if an account already exists with this email or id
    req_data = dict(request.form)

    if len(db.read(db_requests.GET_USER_INFO_BY_MAIL.format(
           mail=req_data['mail']))) != 0:
        return make_response("MAIL ALREADY BOUND", 400)

    try: 
        profileId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(
            name=req_data['profiles']))[0][0]
    except (IndexError, KeyError):
        return make_response("BAD REQUEST", 400)
        
    pswdHash, salt = Auth.hash_password(req_data['pswd'])

    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", request.form.get('phone', default='none')):
        return make_response("INCORRECT TEL", 400)
    
    base_login = req_data['fname'][0].lower() + req_data['lname'].lower()
    login = base_login
    counter = 0

    # Vérifier si l'identifiant existe et l'incrémenter si nécessaire
    while db.read(db_requests.CHECK_LOGIN_EXISTS.format(login=login))[0][0] == 1:
        login = base_login + str(counter)
        counter += 1


    r = api.post_api(apiUrls.POST_USER, payload={
        "firstname": str(req_data['fname']),
        "lastname": str(req_data['lname']),
        "email": str(req_data['mail']),
        "license_plates": [req_data['plate']],
        "contracts": [api.contract['_id']],
        "user_groups": [],
        "hierarchical_level": 3,
        "has_unlimited_geographical_access": True
    })

    if r.status_code == 200:
        db.write(db_requests.INSERT_USER.format(
            id=r.json()['_id'],
            firstname=str(req_data['fname']),
            lastname=str(req_data['lname']),
            mail=str(req_data['mail']),
            phone=str(req_data['phone']),
            usrType=profileId,
            entityId=req_data['entity']))
        
        db.write(db_requests.INSERT_USER_PLATE.format(
            usrId=r.json()['_id'],
            plate=req_data['plate']))

        db.write(db_requests.INSERT_USER_CREDENTIALS.format(
            id=r.json()['_id'], login=login, pswdHash=pswdHash, salt=salt))

        return make_response(render_template('new-account-success.html', connected=False, login=login), 201)
    else:
        return make_response("API ERROR", 400)
    
@app.route('/adminPannel/newaccount', methods=['POST'])
def adminSubmitAccount():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    # Check if an account already exists with this email or id
    req_data = dict(request.form)

    # Get admin entity
    try:
        entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_id))[0][0]
    except:
        return make_response("BAD REQUEST", 400)

    if len(db.read(db_requests.GET_USER_INFO_BY_MAIL.format(
           mail=req_data['mail']))) != 0:
        return make_response("L'adresse mail est déjà associée à un compte", 400)

    try: 
        profileId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(
            name=req_data['profiles']))[0][0]
    except (IndexError, KeyError):
        return make_response("BAD REQUEST", 400)
        
    pswdHash, salt = Auth.hash_password(req_data['pswd'])

    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", request.form.get('phone', default='none')):
        return make_response("Le format du numéro de téléphone est incorrect", 400)

    base_login = req_data['fname'][0].lower() + req_data['lname'].lower()
    login = base_login
    counter = 0

    # Vérifier si l'identifiant existe et l'incrémenter si nécessaire
    while db.read(db_requests.CHECK_LOGIN_EXISTS.format(login=login))[0][0] == 1:
        login = base_login + str(counter)
        counter += 1
    
    r = api.post_api(apiUrls.POST_USER, payload={
        "firstname": str(req_data['fname']),
        "lastname": str(req_data['lname']),
        "email": str(req_data['mail']),
        "license_plates": [],
        "contracts": [api.contract['_id']],
        "user_groups": [],
        "hierarchical_level": 3,
        "has_unlimited_geographical_access": True
    })

    if r.status_code == 200:
        db.write(db_requests.INSERT_USER.format(
            id=r.json()['_id'],
            firstname=str(req_data['fname']),
            lastname=str(req_data['lname']),
            mail=str(req_data['mail']),
            phone=str(req_data['phone']),
            usrType=profileId,
            entityId=entity))

        # Insert plate if request has
        plate = str(req_data['plate'])
        if plate != '' and match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
            db.write(db_requests.INSERT_USER_PLATE.format(usrId=r.json()['_id'], plate=plate))

        db.write(db_requests.INSERT_USER_CREDENTIALS.format(
            id=r.json()['_id'], login=login, pswdHash=pswdHash, salt=salt))

        return make_response("CREATED", 201)
    return make_response("API ERROR", 400)

@app.route('/superAdminPannel/newaccount', methods=['POST'])
def superAdminSubmitAccount():
    token = request.cookies.get("SESSID", default=None)

    admin_id = Auth.is_auth(token, db)

    if admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    # Check if an account already exists with this email or id
    req_data = dict(request.form)

    if len(db.read(db_requests.GET_USER_INFO_BY_MAIL.format(
           mail=req_data['mail']))) != 0:
        return make_response("L'adresse mail est déjà associée à un compte", 400)
        
    try:
        profileId = req_data['profiles']
    except (IndexError, KeyError):
        return make_response("Le profil est incorrect", 400)
        
    pswdHash, salt = Auth.hash_password(req_data['pswd'])

    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", request.form.get('phone', default='none')):
        return make_response("Le format du numéro de téléphone est incorrect", 400)

    base_login = req_data['fname'][0].lower() + req_data['lname'].lower()
    login = base_login
    counter = 0

    # Vérifier si l'identifiant existe et l'incrémenter si nécessaire
    while db.read(db_requests.CHECK_LOGIN_EXISTS.format(login=login))[0][0] == 1:
        login = base_login + str(counter)
        counter += 1

    r = api.post_api(apiUrls.POST_USER, payload={
        "firstname": str(req_data['fname']),
        "lastname": str(req_data['lname']),
        "email": str(req_data['mail']),
        "license_plates": [],
        "contracts": [api.contract['_id']],
        "user_groups": [],
        "hierarchical_level": 3,
        "has_unlimited_geographical_access": True
    })

    if r.status_code != 200:
        return make_response("API ERROR", 500)
    db.write(db_requests.INSERT_USER.format(
        id=r.json()['_id'],
        firstname=str(req_data['fname']),
        lastname=str(req_data['lname']),
        mail=str(req_data['mail']),
        phone=str(req_data['phone']),
        usrType=profileId,
        entityId=str(req_data['entity'])))

    # Insert plate if request has
    plate = str(req_data['plate'])
    if plate != '' and match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
        db.write(db_requests.INSERT_USER_PLATE.format(usrId=r.json()['_id'], plate=plate))

    db.write(db_requests.INSERT_USER_CREDENTIALS.format(
            id=r.json()['_id'], login=login, pswdHash=pswdHash, salt=salt))

    return make_response("CREATED", 201)

@app.route('/superAdminPannel/newadminaccount', methods=['POST'])
def superAdminSubmitAdminAccount():
    token = request.cookies.get("SESSID", default=None)

    super_admin_id = Auth.is_auth(token, db)

    if super_admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(super_admin_id, db):
        return make_response("UNAUTHORIZED", 401)
    
        # Check if an account already exists with this email or id
    req_data = dict(request.form)

    if len(db.read(db_requests.GET_USER_INFO_BY_MAIL.format(
           mail=req_data['mail']))) != 0:

        return make_response("L'adresse mail est déjà enregistrée", 400)

    try: 
        profileId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(
            name=req_data['profiles']))[0][0]
    except (IndexError, KeyError):
        return make_response("Le profil est incorrect", 400)
        
    pswdHash, salt = Auth.hash_password(req_data['pswd'])

    if not match("^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", request.form.get('phone', default='none')):
        return make_response("Le format du numéro de téléphone est incorrect", 400)

    base_login = req_data['fname'][0].lower() + req_data['lname'].lower()
    login = base_login
    counter = 0

    # Vérifier si l'identifiant existe et l'incrémenter si nécessaire
    while db.read(db_requests.CHECK_LOGIN_EXISTS.format(login=login))[0][0] == 1:
        login = base_login + str(counter)
        counter += 1

    r = api.post_api(apiUrls.POST_USER, payload={
        "firstname": str(req_data['fname']),
        "lastname": str(req_data['lname']),
        "email": str(req_data['mail']),
        "license_plates": [],
        "contracts": [api.contract['_id']],
        "user_groups": [],
        "hierarchical_level": 3,
        "has_unlimited_geographical_access": True
    })

    if r.status_code != 200:
        return make_response("API ERROR", 500)
    
    db.write(db_requests.INSERT_ADMIN_USER.format(
        id=r.json()['_id'],
        firstname=str(req_data['fname']),
        lastname=str(req_data['lname']),
        mail=str(req_data['mail']),
        phone=str(req_data['phone']),
        usrType=profileId,
        entityId=str(req_data['entity'])))

    # Insert plate if request has
    plate = str(req_data['plate'])
    if plate != '' and (match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate)):
        db.write(db_requests.INSERT_USER_PLATE.format(usrId=r.json()['_id'], plate=plate))

    db.write(db_requests.INSERT_USER_CREDENTIALS.format(
            id=r.json()['_id'], login=login, pswdHash=pswdHash, salt=salt))

    return make_response("CREATED", 201)

@app.route('/profiles', methods=['GET'])
def getProfiles():
    entity_arg = request.args.get('entity', default=None)
    
    if entity_arg is None:
        return make_response('BAD REQUEST', 400)
    
    profiles_entity = [p[0] for p in db.read(db_requests.GET_PROFILES_NAMES_BY_ENTITY.format(entityId=str(entity_arg)))]

    return make_response(profiles_entity, 200)

@app.route('/resetpswd', methods=['GET'])
def reset_pswd():
    return render_template('reset-pswd.html', connected=False)

@app.route('/resetpswd/request', methods=['POST'])
def request_reset_pswd():
    mail = request.form.get("mail", default=None)

    if mail is None:
        return make_response("BAD REQUEST", 400)

    user = db.read(db_requests.GET_USER_INFO_BY_MAIL.format(mail=mail))
    
    if len(user) == 0:
        return make_response("OK", 200)
    user = user[0]

    reset_token = Auth.hash_password(user[0] + user[1] + user[2])[0]

    # Delete older request
    db.write(db_requests.DELETE_USER_PASSWORD_RESET_REQUEST.format(usrId=user[0]))

    db.write(db_requests.INSERT_RESET_PSWD.format(usrToken=reset_token, usrId=user[0]))

    mailInterface = Mailling(mail_host, mail_pswd)

    try:
        mailInterface.connect()

        mail_text = mailInterface.buildmail(
            mail,
            mails.RESET_PSWD_REQUEST["subject"],
            mails.RESET_PSWD_REQUEST["content"].format(reset_link=BASE_APP_URL + "/resetpswd/" + reset_token),
            imagePath)
        mailInterface.sendmail(mail, mail_text)
        return make_response("OK", 200)
    except Exception as e:
        print(e)
        return make_response("NETWORK ERROR", 500)

@app.route('/resetpswd/<string:resettoken>', methods=['GET'])
def reset_pswd_action(resettoken):
    # Check if we have a request for this token
    usr = db.read(db_requests.GET_PASSWORD_RESET_REQUEST.format(token=resettoken))

    if len(usr) == 0:
        return make_response("NOT FOUND", 404)

    return render_template("reset-pswd-action.html", resettoken=resettoken)

@app.route('/resetpswd/<string:resettoken>', methods=['POST'])
def reset_pswd_post(resettoken):
    # Check if we have a request for this token
    usr = db.read(db_requests.GET_PASSWORD_RESET_REQUEST.format(token=resettoken))

    if len(usr) == 0:
        return make_response("NOT FOUND", 404)
    
    usr = usr[0]
    
    pswd = request.form.get("pswd", default=None)
    pswd_confirm = request.form.get("pswd-confirm", default=None)

    if pswd is None or pswd_confirm is None or pswd != pswd_confirm:
        return make_response("BAD REQUEST", 400)

    pswdHash, salt = Auth.hash_password(pswd)

    # Update db entry
    db.write(db_requests.UPDATE_PASSWORD_CREDENTIALS.format(pswdHash=pswdHash, salt=salt, usrId=usr[1]))

    # Remove reset token
    db.write(db_requests.DELETE_USER_PASSWORD_RESET_REQUEST.format(usrId=usr[1]))

    return make_response("OK", 200)

@app.route('/account', methods=['GET'])
def get_account():
    auth_token = request.cookies.get('SESSID', default=None)

    if auth_token == None:
        return redirect(url_for('login'))

    db_id = db.read(
        db_requests.GET_USER_ID_FROM_TOKEN.format(token=auth_token))

    if len(db_id) <= 0:
        return redirect(url_for('login'))
    else:
        db_id = db_id[0][0]

    # Fetch user info
    user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=db_id))[0]
    userPlates = [e[0] for e in db.read(
        db_requests.GET_USER_PLATES.format(usrId=db_id))]

    profileType = db.read(
        db_requests.GET_PROFILE_NAME_BY_ID.format(id=user[4]))[0][0]

    if user[5] == 0:
        profileState = "pending"
        profileStateIcon = img.PENDING["img"]
        profileStateAlt = img.PENDING["alt"]
    elif user[5] == 1:
        profileState = "valid"
        profileStateIcon = img.VALID["img"]
        profileStateAlt = img.VALID["alt"]
    else:
        profileState = "invalid"
        profileStateIcon = img.REFUSED["img"]
        profileStateAlt = img.REFUSED["alt"]

    payload = {
        "lastname": user[1],
        "firstname": user[0],
        "mail": user[2],
        "hasPhone": user[3] != None,
        "phone": ' '.join([user[3][i:i+2] for i in range(0, len(user[3]), 2)]) if user[3] != None else "none",
        "plates": userPlates,
        "state": profileState,
        "profileType": profileType,
        "profileStateIconPath": profileStateIcon,
        "profileStateIconAlt": profileStateAlt,
        "profileTypeLabel": profileStateAlt
    }

    return render_template('account.html', connected=True, **payload, isAdmin=(user[6] > 0))

@app.route('/editmail', methods=['POST'])
def edit_mail():
    token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(token, db)

    if usr_id is None:
        return redirect(url_for('login'))
    
    newmail = request.form.get('mail', default=None)

    if newmail is None:
        return make_response("BAD REQUEST", 400)
    
    if db.read(db_requests.IS_MAIL_EXISTS.format(mail=newmail))[0][0] == 1:
        return make_response("MAIL ALREADY BOUND", 403)
    
    r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usr_id}, data_payload={'email':newmail, 'contracts':[api.contract['_id']]})
    if r.status_code == 200:
        db.write(db_requests.UPDATE_USER_MAIL.format(mail=newmail, usrId=usr_id))

        if db.read(db_requests.GET_USER_HIERARCHICAL_LEVEL.format(usrId=usr_id))[0][0] > 0:
            db.write(db_requests.CONFIRM_USER.format(usrId=usr_id))
        else :
            db.write(db_requests.UPDATE_USER_APPROBATION.format(usrId=usr_id, approbation=0))

            mailInterface = Mailling(mail_host, mail_pswd)
            mail = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=usr_id))[0][2]

            try:
                mailInterface.connect()

                mail_text = mailInterface.buildmail(
                    mail,
                    mails.ASK_UPDATE_ACCOUNT["subject"],
                    mails.ASK_UPDATE_ACCOUNT["content"],
                    imagePath)
                mailInterface.sendmail(mail, mail_text)
                return make_response("OK", 200)
            except Exception as e:
                print(e)
                return make_response("NETWORK ERROR", 500)

        
        return make_response("OK", 200)
    else:
        return make_response("API ERROR", 500)

@app.route('/addplate', methods=['POST'])
def add_plate():
    plate = request.form.get('plate').upper()

    # Check if plate respect format
    if match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
        # Plate if good, new line in database (see below)
        # Fetch user
        authToken = request.cookies.get('SESSID', default=None)

        # Read User id
        usr_id = db.read(
            db_requests.GET_USER_ID_FROM_TOKEN.format(token=authToken))[0][0]

        # Check if user doesnt have already 2 plates
        n_plate = db.read(db_requests.GET_USER_PLATES_COUNT.format(usrId=usr_id))[0][0]
        
        if n_plate >= 2:
            return make_response("FORBIDDEN", 403)

        # Try to write plate in db
        # If plate already exists, it leaves an IntegrityError from mysql
        # In that case we return a 409 CONFLIT to the Client
        try:
            db.write(db_requests.INSERT_USER_PLATE.format(
                usrId=usr_id, plate=plate))
            
            if db.read(db_requests.GET_USER_HIERARCHICAL_LEVEL.format(usrId=usr_id))[0][0] == 0:
                db.write(db_requests.UPDATE_USER_APPROBATION.format(usrId=usr_id, approbation=0))

                mailInterface = Mailling(mail_host, mail_pswd)
                mail = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=usr_id))[0][2]

                try:
                    mailInterface.connect()

                    mail_text = mailInterface.buildmail(
                        mail,
                        mails.ASK_UPDATE_ACCOUNT["subject"],
                        mails.ASK_UPDATE_ACCOUNT["content"],
                        imagePath)
                    mailInterface.sendmail(mail, mail_text)
                    return make_response("OK", 200)
                except Exception as e:
                    print(e)
                    return make_response("NETWORK ERROR", 500)
            
            r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usr_id}, data_payload={
                        "license_plates": [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=usr_id))],
                        "contracts": [api.contract["_id"]],
                })
            if r.status_code != 200:
                db.write(db_requests.DELETE_PLATE.format(
                usrId=usr_id, plate=plate))
                return make_response("API ERROR", 500)

                  
        except IntegrityError:
            return make_response('PLATE ALREADY KNOWN', 409)

        # Insert is OK we return a 201 CREATED to client
        return make_response('OK', 201)

    else:
        # Plate doesn't respect standard, return a 400 BAD REQUEST to the client
        return make_response('PLATE FORMAT ERROR', 400)

@app.route('/fetchplates', methods=['GET'])
def fetch_plates():
    token = request.cookies.get('SESSID', default=None)

    usr = Auth.is_auth(token, db)

    if usr is None:
        return make_response('INVALID TOKEN', 403)

    a = db.read(db_requests.GET_USER_APPROBATION.format(usrId=usr))[0][0]
    if a != 1:
        return make_response("UNAUTHORIZED", 401)

    usr_plates = [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=usr))]

    return make_response(usr_plates, 200)

@app.route('/deleteplate', methods=['POST'])
def delete_plate():
    token = request.cookies.get('SESSID', default=None)

    usr = Auth.is_auth(token, db)

    if usr is None:
        return make_response('INVALID TOKEN', 403)

    plate = request.form.get('plate', default=None)

    if match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
        try:
            db.write(db_requests.DELETE_PLATE.format(plate=plate, usrId=usr))

            r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usr}, data_payload={
                        "license_plates": [p[0] for p in db.read(db_requests.GET_USER_PLATES.format(usrId=usr))],
                        "contracts": [api.contract["_id"]],
                })
            
            if r.status_code != 200:
                return make_response("API ERROR", 500)
        except IntegrityError:
            return make_response('CONFLICT', 409)
        return make_response('OK', 200)
    else:
        return make_response('PLATE FORMAT ERROR', 400)
    
@app.route('/superAdminPannel/allocation/addEntity', methods=['POST'])
def superAdminAddEntity():
    token = request.cookies.get('SESSID', default=None)

    super_admin_id = Auth.is_auth(token, db)

    if super_admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(super_admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    entity_name = request.form.get('name', default=None)
    entity_nbPlacesAllocated = request.form.get('nbPlacesAllocated', default=None)
    entity_nbFreePlaces = 100
    nbFreePlaces = request.form.get('nbFreePlaces', default=None)

    try:
        entity_nbPlacesAllocated = int(entity_nbPlacesAllocated)
        nbFreePlaces = int(nbFreePlaces)
    except ValueError:
        return make_response("Invalid number of places allocated", 400)

    if entity_name is None:
        return make_response("BAD REQUEST", 400)
    
    if entity_nbPlacesAllocated < 0 or entity_nbPlacesAllocated > nbFreePlaces:
        return make_response("Invalid number of places allocated", 400)

    existing_ids = db.read(db_requests.GET_ALL_ENTITIES_IDS)
    max_id_number = 0

    # Récupérer tous les ID d'entités existants
    for entity_id in existing_ids:
        try:
            id_number = int(entity_id[0].replace("id", ""))
            if id_number > max_id_number:
                max_id_number = id_number
        except ValueError:
            continue 

    new_id = "id" + str(max_id_number + 1)

    db.write(db_requests.INSERT_ENTITY.format(id=new_id, eName=entity_name, nbPlacesAllocated=entity_nbPlacesAllocated, nbFreePlaces=entity_nbFreePlaces))

    return make_response("OK", 200)

@app.route('/superAdminPannel/allocation/deleteEntity', methods=['POST'])
def superAdminDeleteEntity():
    token = request.cookies.get('SESSID', default=None)

    super_admin_id = Auth.is_auth(token, db)

    if super_admin_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_super_admin(super_admin_id, db):
        return make_response("UNAUTHORIZED", 401)

    entity_id = request.form.get('id', default=None)

    if entity_id is None:
        return make_response("BAD REQUEST", 400)

    db.write(db_requests.DELETE_ENTITY.format(id=entity_id))

    return make_response("OK", 200)

@app.route('/getbooking', methods=['GET'])
def get_booking():
    token = request.cookies.get("SESSID", default=None)

    usr = Auth.is_auth(token, db)

    if usr is None:
        return redirect(url_for('login'), 302)
    
    bId = str(request.args.get("bookingID", default=''))

    f = db.read(db_requests.GET_BOOKING_FROM_ID.format(uuid=bId, usrId=usr))
    
    if len(f) < 1:
        return make_response("NO BOOKING", 404)
    f = f[0]
    booking = {
        'bookingID': f[0],
        'bookingPlate': f[2],
        'bookingPresent': f[3],
        'bookingStart': f[4],
        'bookingEnd': f[5],
        'bookingRepeat': f[6],
        'bookingRepeatCustomInterval': f[7],
        'bookingRepeatCustomAmount': f[8],
        'bookingRepeatCustomMonday': f[9],
        'bookingRepeatCustomTuesday': f[10],
        'bookingRepeatCustomWednesday': f[11],
        'bookingRepeatCustomThursday': f[12],
        'bookingRepeatCustomFriday': f[13],
        'bookingRepeatCustomSaturday': f[14],
        'bookingRepeatCustomSunday': f[15],
        'bookingRepeatEnding': f[16],
        'criticity': f[17]
    }

    return make_response(booking, 200)

@app.route('/addbooking', methods=['POST'])
def add_booking():
    try:
        token = request.cookies.get('SESSID', default=None)
        usr = Auth.is_auth(token, db)
        if usr is None:
            return redirect(url_for('login'), 302)

        if db.read(db_requests.GET_USER_APPROBATION.format(usrId=usr))[0][0] != 1:
            return make_response("LOCKED", 423)

        plate = request.form.get('plate').upper()
        startDatetime = request.form.get('booking-start')
        endDateTime = request.form.get('booking-end')
        interval = request.form.get('interval')
        ending = request.form.get("ending")

        bypass = True if db.read(db_requests.GET_USER_HIERARCHICAL_LEVEL.format(usrId=usr))[0][0] == 2 else False

        # Corrected regular expression to match times without leading zero in hours
        datetime_pattern = '^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) ([01]?[0-9]|2[0-3]):[0-5][0-9]:00\.000000$'
        start_match = re.match(datetime_pattern, startDatetime)
        end_match = re.match(datetime_pattern, endDateTime)
        ending_match = re.match(datetime_pattern, ending) if ending else True
        plate_pattern = '^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$'
        plate_match = re.match(plate_pattern, plate) or re.match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate)

        if start_match and end_match and ending_match and plate_match:
            if interval in ['unique', 'daily', 'weekly', 'monthly']:
                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending, bypass=bypass)
                if success:
                    return make_response('CREATE SUCCESSFUL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

            elif interval == 'custom':
                customInterval = request.form.get('customInterval', default=None)
                if customInterval is None or customInterval not in ["day", "week", "month"]:
                    return make_response('INVALID DATA', 400)
                try:
                    customAmount = int(request.form.get('customAmount', default=None))
                except (TypeError, ValueError):
                    return make_response('INVALID DATA', 400)
                monday = 1 if request.form.get('monday', default=False) == "true" else 0
                tuesday = 1 if request.form.get('tuesday', default=False) == "true" else 0
                wednesday = 1 if request.form.get('wednesday', default=False) == "true" else 0
                thursday = 1 if request.form.get('thursday', default=False) == "true" else 0
                friday = 1 if request.form.get('friday', default=False) == "true" else 0
                saturday = 1 if request.form.get('saturday', default=False) == "true" else 0
                sunday = 1 if request.form.get('sunday', default=False) == "true" else 0
                if ending is None or not re.match(datetime_pattern, ending):
                    return make_response('INVALID DATA', 400)
                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending, customInterval=customInterval, customAmount=customAmount, repeatMonday=monday, repeatTuesday=tuesday, repeatWednesday=wednesday, repeatThursday=thursday, repeatFriday=friday, repeatSaturday=saturday, repeatSunday=sunday, bypass=bypass)
                if success:
                    return make_response('CREATE SUCCESSFUL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

        return make_response('INVALID DATA', 400)
    except Exception as e:
        return make_response('SERVER ERROR', 500)

@app.route('/adminPannel/addUserBooking', methods=['POST'])
def add_user_booking():
    token = request.cookies.get('SESSID', default=None)

    admin_user = Auth.is_auth(token, db)
    if admin_user is None:
        return redirect(url_for('login'), 302)
    if not Auth.is_admin(admin_user, db):
        return make_response('UNAUTHORIZED', 401)

    usr = request.form.get('usrId')
    plate = request.form.get('plate').upper()
    startDatetime = request.form.get('booking-start')
    endDateTime = request.form.get('booking-end')
    interval = request.form.get('interval')
    ending = request.form.get("ending")

    if match('^[0-9]{4}-(0|1)[0-9]-(0|1|2|3)[0-9] (0|1|2)[0-9]:[0-6][0-9]:00.000000', startDatetime) and match('^[0-9]{4}-(0|1)[0-9]-(0|1|2)[0-9]:[0-6][0-9]:00.000000', endDateTime) and match('^[0-9]{4}-(0|1)[0-9]-(0|1|2)[0-9]:[0-6][0-9]:00.000000', ending):
        if match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
            if interval == 'unique' or interval == 'daily' or interval == 'weekly' or interval == 'monthly':
                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending)
                if success:
                    return make_response('CREATE SUCCESSFUL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

            elif interval == 'custom':
                customInterval = request.form.get('customInterval', default=None)
                if customInterval is None or customInterval not in ["day", "week", "month"]:
                    return make_response('INVALID DATA', 400)
                try:
                    customAmount = int(request.form.get('customAmount', default=None))
                except TypeError:
                    return make_response('INVALID DATA', 400)
                monday = 1 if request.form.get('monday', default=False) == "true" else 0
                tuesday = 1 if request.form.get('tuesday', default=False) == "true" else 0
                wednesday = 1 if request.form.get('wednesday', default=False) == "true" else 0
                thursday = 1 if request.form.get('thursday', default=False) == "true" else 0
                friday = 1 if request.form.get('friday', default=False) == "true" else 0
                saturday = 1 if request.form.get('saturday', default=False) == "true" else 0
                sunday = 1 if request.form.get('sunday', default=False) == "true" else 0
                ending = request.form.get('ending')
                if ending is None or not match('^[0-9]{4}-(0|1)[0-9]-(0|1|2)[0-9]:[0-6][0-9]:00.000000', ending):
                    return make_response('INVALID DATA', 400)
                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending, customInterval=customInterval, customAmount=customAmount, repeatMonday=monday, repeatTuesday=tuesday, repeatWednesday=wednesday, repeatThursday=thursday, repeatFriday=friday, repeatSaturday=saturday, repeatSunday=sunday)
                if success:
                    return make_response('CREATE SUCCESSFUL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

    return make_response('INVALID DATA', 400)

@app.route('/superAdminPannel/addUserBooking', methods=['POST'])
def superAddUserBooking():
    token = request.cookies.get('SESSID', default=None)

    # Récupérer les places disponibles sur la période de temps
    """
    
    PARTIE API:
        - Récupération disponibilité et retours à l'utilisateur
        - Vérification si périodicité est valide sur la période demandée (nécessite de changer la db et d'orienter les tables sur des plages de temps)
    
    """

    admin_user = Auth.is_auth(token, db)

    if admin_user is None:
        return redirect(url_for('login'), 302)

    if not Auth.is_super_admin(admin_user, db):
        return make_response('UNAUTHORIZED', 401)


    usr = request.form.get('usrId')
    plate = request.form.get('plate').upper()
    startDatetime = request.form.get('booking-start')
    endDateTime = request.form.get('booking-end')
    interval = request.form.get('interval')
    ending = request.form.get("ending");

    if match('^[0-9]{4}-(0|1)[0-9]-(0|1|2|3)[0-9] (0|1|2)[0-9]:[0-6][0-9]:00.000000', startDatetime) and match('^[0-9]{4}-(0|1)[0-9]-(0|1|2|3)[0-9] (0|1|2)[0-9]:[0-6][0-9]:00.000000', endDateTime) and match('^[0-9]{4}-(0|1)[0-9]-(0|1|2|3)[0-9] (0|1|2)[0-9]:[0-6][0-9]:00.000000', ending):
        # Datetimes match
        if match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) or match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate):
            # Plates match

            if interval == 'unique' or interval == 'daily' or interval == 'weekly' or interval == 'monthly':
                # Write booking
                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending)
                
                if success:
                    return make_response('CREATE SUCCESSFULL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

            elif interval == 'custom':
                # Read custom interval properties

                customInterval = request.form.get('customInterval', default=None)

                if customInterval == None or (customInterval != "day" and customInterval != "week" and customInterval != "month"):
                    return make_response('INVALID DATA', 400)

                try:
                    customAmount = int(request.form.get('customAmount', default=None))
                except TypeError:
                    return make_response('INVALID DATA', 400)

                # Make sure data injected in db is what we want to, not a string or smth else
                monday = 1 if request.form.get('monday', default=False) == "true" else 0
                tuesday = 1 if request.form.get('tuesday', default=False) == "true" else 0
                wednesday = 1 if request.form.get('wednesday', default=False) == "true" else 0
                thursday = 1 if request.form.get('thursday', default=False) == "true" else 0
                friday = 1 if request.form.get('friday', default=False) == "true" else 0
                saturday = 1 if request.form.get('saturday', default=False) == "true" else 0
                sunday = 1 if request.form.get('sunday', default=False) == "true" else 0
                ending = request.form.get('ending')

                if ending == None or not match('^[0-9]{4}-(0|1)[0-9]-(0|1|2|3)[0-9] (0|1|2)[0-9]:[0-6][0-9]:00.000000', ending):
                    return make_response('INVALID DATA', 400)

                success, err = Book.book(api, db, usr, plate, startDatetime, endDateTime, interval, ending, customInterval=customInterval, customAmount=customAmount, repeatMonday=monday, repeatTuesday=tuesday, repeatWednesday=wednesday, repeatThursday=thursday, repeatFriday=friday, repeatSaturday=saturday, repeatSunday=sunday)
                
                if success:
                    return make_response('CREATE SUCCESSFULL', 201)
                else:
                    return make_response(f'Error: {err}', 500)

    # In all others cases it's an invalid data
    return make_response('INVALID DATA', 400)

@app.route("/deletebooking", methods=["DELETE"])
def delete_booking():
    token = request.cookies.get('SESSID', default=None)

    usr = Auth.is_auth(token, db)

    if usr is None:
        return make_response('INVALID TOKEN', 403)

    booking_id = request.form.get('id')

    if booking_id is None:
        return make_response('INVALID', 400)

    Book.delete_booking(api, db, booking_id, usr)
    return make_response('DELETE SUCCESSFULL', 200)

@app.route("/adminPannel/deleteUserBooking", methods=["DELETE"])
def delete_user_booking():
    token = request.cookies.get('SESSID', default=None)

    admin_usr = Auth.is_auth(token, db)

    if admin_usr is None:
        return make_response('INVALID TOKEN', 403)

    if not Auth.is_admin(admin_usr, db):
        return make_response('UNAUTHORIZED', 401)

    booking_id = request.form.get('id')
    usr_id = request.form.get('usrId')

    if booking_id is None or usr_id is None:
        return make_response('BAD REQUEST', 400)
    
    # Check entity
    if db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=admin_usr)) != db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usr_id)):
        return make_response('UNAUTHORIZED', 401)

    Book.delete_booking(api, db, booking_id, usr_id)
    return make_response('DELETE SUCCESSFULL', 200)

@app.route("/superAdminPannel/deleteUserBooking", methods=["DELETE"])
def superDeleteUserBooking():
    token = request.cookies.get('SESSID', default=None)

    admin_usr = Auth.is_auth(token, db)

    if admin_usr is None:
        return make_response('INVALID TOKEN', 403)

    if not Auth.is_super_admin(admin_usr, db):
        return make_response('UNAUTHORIZED', 401)

    booking_id = request.form.get('id')
    usr_id = request.form.get('usrId')

    if booking_id is None or usr_id is None:
        return make_response('BAD REQUEST', 400)
    
    Book.delete_booking(api, db, booking_id, usr_id)
    return make_response('DELETE SUCCESSFULL', 200)

@app.route('/critical/open', methods=['GET'])
def critical_opening():
    auth_token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(auth_token, db)

    if usr_id is None:
        return redirect(url_for('login'))

    if not Auth.is_admin(usr_id, db) and not Auth.is_super_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)
    
    # Open api request
    #r1 = api.post_api(apiUrls.POST_FORCE_OPEN_ACCESS, path_payload={'id': '63e5027875729c00bf3ec7b9'})
    #r2 = api.post_api(apiUrls.POST_FORCE_OPEN_ACCESS, path_payload={'id': '63e5028d75729c00bf3ec7bc'})

    r1 = api.post_api(apiUrls.POST_OPEN_ACCESS, path_payload={'id': '63e5027875729c00bf3ec7b9'}, payload={'location': {'lat': 50.6510382372813, 'lng': 2.96874134678398}})
    r2 = api.post_api(apiUrls.POST_OPEN_ACCESS, path_payload={'id': '63e5028d75729c00bf3ec7bc'}, payload={'location': {'lat': 50.65103823728132, 'lng': 2.9687413467839767}})

    print(r1, r1.text)
    print(r2, r2.text)

    if r1.status_code == 204 and r2.status_code == 204:
        return make_response('OK', 200)
    else:
        return make_response('API ERROR', 500)

@app.route('/admin/notifications', methods=['GET'])
def admin_notifications():
    token = request.cookies.get('SESSID', default=None)

    usr_id = Auth.is_auth(token, db)

    if usr_id is None:
        return redirect(url_for('login'))
    
    if not Auth.is_admin(usr_id, db) and not Auth.is_super_admin(usr_id, db):
        return make_response('UNAUTHORIZED', 401)

    alerts = db.read(db_requests.GET_RAW_ALERTS)

    unique_plates = set([a[3] for a in alerts])

    payload = {}

    for plate in unique_plates:
        n_alerts = len([a for a in alerts if a[3]==plate])
        if n_alerts >= 2:
            payload[plate] = {
                'plate': plate,
                'count': n_alerts,
                'alerts': list()
            }

    for a in alerts:
        if not a[3] in payload.keys():
            continue
        alert_type = "absent"
        if a[1] == 1:
            alert_type = "earlier"
        elif a[1] == 2:
            alert_type = "earlier-2"
        elif a[2] == 1:
            alert_type = "later"
        elif a[2] == 2:
            alert_type = "later-2"

        payload[a[3]]['alerts'].append({
            "type": alert_type,
            "user": f"{a[4]} {a[5]}",
            "plate": a[3],
            "start": a[6],
            "end": a[7],
            "created": a[8]
        })

    if Auth.is_admin(usr_id, db):
        return render_template('notifications.html', connected=True, notif_count=len(payload.keys()), notifications=payload, adminHeadline="Direction", adminRoute="adminPannel")
    elif Auth.is_super_admin(usr_id, db):
        return render_template('notifications.html', connected=True, notif_count=len(payload.keys()), notifications=payload, adminHeadline="Administration", adminRoute="superAdminPannel")
    else:
        return make_response("UNAUTHORIZED", 401)

@app.route('/admin/notification/delete', methods=['POST'])
def admin_notifications_delete():
    token = request.cookies.get("SESSID", default=None)

    usr_id = Auth.is_auth(token, db)
        
    if usr_id is None:
        return redirect(url_for('login'), 302)

    if (not Auth.is_admin(usr_id, db)) and (not Auth.is_super_admin(usr_id, db)):
        return make_response('UNAUTHORIZED', 401)
    
    plate = request.form.get("plate", default=None)

    if plate is None:
        return make_response("BAD REQUEST", 400)
    
    db.write(db_requests.DELETE_ALERTS_BY_PLATE.format(plate=plate))

    return make_response("OK", 200)

""" Stats endpoints """
@app.route('/stats/fillrate/hourly', methods=['GET'])
def get_fillrate_stats_hourly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)
    delta = to_timestamp - from_timestamp

    if delta <= 0:
        return make_response("BAD REQUEST", 400)

    n_hours = delta // 3600

    from_date = datetime.fromtimestamp(int(from_timestamp))

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    labels = []
    for _ in range(n_hours):
        labels.append(days[from_date.weekday()] + " " + str(from_date.hour) + "h")
        from_date = from_date + timedelta(hours=1)
    
    data = []
    for i in range(n_hours)[::24]:
        r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp+i*3600, 'to': to_timestamp-(n_hours-i-24+1)*3600, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'HOUR'})
        if (r.status_code != 200):
            return make_response("API ERROR", 500)
        
        data += list(r.json()['real_time'].values())


    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/fillrate/daily', methods=['GET'])
def get_fillrate_stats_daily():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_days = (int(to_timestamp) - int(from_timestamp)) // 86400

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_days):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(days=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})
    
    if (r.status_code != 200):
        return make_response("API ERROR", 500)

    return make_response(jsonify({'data': list(r.json()['real_time'].values()), 'labels': labels}), 200)

@app.route('/stats/fillrate/weekly', methods=['GET'])
def get_fillrate_stats_weekly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_weeks = (int(to_timestamp) - int(from_timestamp)) // 604800

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_weeks):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(weeks=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    week_sum = 0
    values = list(r.json()['real_time'].values())
    data = []
    for i in range(len(values)):
        if i%7 == 0 and i != 0:
            data.append(week_sum)
            week_sum = 0

        week_sum += values[i]

    data.append(week_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/fillrate/monthly', methods=['GET'])
def get_fillrate_stats_monthly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if from_timestamp is None or to_timestamp is None:
        return make_response("BAD REQUEST", 400)
    
    n_months = (int(to_timestamp) - int(from_timestamp)) // 2592000

    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    from_date = datetime.fromtimestamp(int(from_timestamp))
    data = []
    labels = []
    value_index_offset = 0
    values = list(r.json()['real_time'].values())
    for _ in range(n_months):
        end_month_day = calendar.monthrange(from_date.year, from_date.month)[1]

        labels.append(months[from_date.month-1])
        from_date = from_date + timedelta(days=end_month_day)
        month_sum = 0
        for v in values[value_index_offset:value_index_offset+end_month_day]:
            month_sum += v
        value_index_offset += end_month_day
        data.append(month_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/parkusage', methods=['GET'])
def get_parkusage_stats():
    today = date.today()
    incrementalDateStart = date(today.year-1, today.month, 1)
    incrementalDateEnd = date(today.year-1, today.month, calendar.monthrange(today.year-1, today.month)[1])
    
    startTS = datetime.combine(incrementalDateStart, datetime.min.time())
    endTS = datetime.combine(incrementalDateEnd, datetime.min.time())
    
    data = []
    for _ in range(12):
        end_month_day = calendar.monthrange(startTS.year, startTS.month)[1]
        
        r = statsApi.get_api(statsUrls.GET_GENERAL_STATS_OF_AREA, path_parameters={'id': area_id}, query_payload={'from':startTS.timestamp(), 'to':endTS.timestamp(), 'flow_types':'CAR,TWO_WHEELER,DELIVERY'})
        if r.status_code != 200:
            return make_response("API ERROR", 500)
        
        data.append(r.json()['flow']['in']['value'])

        startTS = startTS + timedelta(days=end_month_day)
        endTS = endTS + timedelta(days=end_month_day)


    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    labels = months[date.today().month - 1::] + months[:date.today().month - 1]

    
    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/realfillrate/hourly', methods=['GET'])
def get_realfillrate_stats_hourly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)

    n_hours = (to_timestamp - from_timestamp) // 3600

    from_date = datetime.fromtimestamp(int(from_timestamp))

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    labels = []
    for _ in range(n_hours):
        labels.append(days[from_date.weekday()] + " " + str(from_date.hour) + "h")
        from_date = from_date + timedelta(hours=1)

    data = []
    for i in range(n_hours)[::24]:
        r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp+i*3600, 'to': to_timestamp-(n_hours-i-24+1)*3600, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'HOUR'})
        if (r.status_code != 200):
            return make_response("API ERROR", 500)
        r_data = r.json()
        data += [v1/v2 if v2 != 0 and not (v1 is None or v2 is None) else 0 for v1, v2 in zip(list(r_data['real_time'].values()), list(r_data['previsional'].values()))]

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/realfillrate/daily', methods=['GET'])
def get_realfillrate_stats_daily():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    from_timestamp = int(from_timestamp)
    to_timestamp = int(to_timestamp)
    delta = to_timestamp - from_timestamp

    if delta <= 0:
        return make_response("BAD REQUEST", 400)

    n_days = delta // 86400

    from_date = datetime.fromtimestamp(from_timestamp)

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(from_timestamp)
    labels = []
    for _ in range(n_days):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(days=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})
    
    if (r.status_code != 200):
        return make_response("API ERROR", 500)

    data = [v1/v2 is not(v1 is None or v2 is None) for v1, v2 in zip(list(r.json()['real_time'].values()), list(r.json()['previsional'].values()))]
    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/realfillrate/weekly', methods=['GET'])
def get_realfillrate_stats_weekly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    n_weeks = (int(to_timestamp) - int(from_timestamp)) // 604800

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    from_date = datetime.fromtimestamp(int(from_timestamp))
    labels = []
    for _ in range(n_weeks):
        labels.append(days[from_date.weekday()] + " " + str(from_date.day))
        from_date = from_date + timedelta(weeks=1)

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    week_sum = 0
    values = list(r.json()['real_time'].values())
    previsional = list(r.json()['previsional'].values())
    data = []
    for i in range(len(values)):
        if i%7 == 0 and i != 0:
            data.append(week_sum)
            week_sum = 0

        if not(values[i] is None or previsional[i] is None):
            week_sum += values[i]/previsional[i]

    data.append(week_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/realfillrate/monthly', methods=['GET'])
def get_realfillrate_stats_monthly():
    from_timestamp = request.args.get("from", default=None)
    to_timestamp = request.args.get("to", default=None)

    if (from_timestamp is None or to_timestamp is None):
        return make_response("BAD REQUEST", 400)
    
    n_months = (int(to_timestamp) - int(from_timestamp)) // 2592000

    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    r = statsApi.get_api(statsUrls.GET_DATA_ATTENDANCE, path_parameters={'id': area_id}, query_payload={'from': from_timestamp, 'to': to_timestamp, 'flow_types': 'CAR,TWO_WHEELER,DELIVERY', 'x_axis': 'DAY'})

    if r.status_code != 200:
        return make_response("API ERROR", 500)

    from_date = datetime.fromtimestamp(int(from_timestamp))
    data = []
    labels = []
    value_index_offset = 0
    values = list(r.json()['real_time'].values())
    previsional = list(r.json()['previsional'].values())
    for _ in range(n_months):
        end_month_day = calendar.monthrange(from_date.year, from_date.month)[1]

        labels.append(months[from_date.month-1])
        from_date = from_date + timedelta(days=end_month_day)
        month_sum = 0
        for v, p in zip(values[value_index_offset:value_index_offset+end_month_day], previsional[value_index_offset:value_index_offset+end_month_day]):
            month_sum += v/p
        value_index_offset += end_month_day
        data.append(month_sum)

    return make_response(jsonify({'data': data, 'labels': labels}), 200)

@app.route('/stats/parkduration/plate', methods=['GET'])
def get_parkduration_plate():
    plate = request.args.get('plate', default=None)

    if plate is None or (not match('^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', plate) and not match('^[0-9]{4}-[A-Z]{2}-[0-9]{2}$', plate)):
        return make_response("BAD REQUEST", 400)
    
    records_in = db_flow.read(db_requests.GET_PLATE_IN_DATETIMES_RECORDS.format(plate=plate))
    records_out = db_flow.read(db_requests.GET_PLATE_OUT_DATETIMES_RECORDS.format(plate=plate))

    payload = {}

    duration = timedelta(days=0)
    for i in range(min(len(records_in), len(records_out))):
        duration += records_out[i][1] - records_in[i][1]
    
    present = len(records_in) == len(records_out)+1

    payload["duration"] = {
                "days": duration.days,
                "hours": duration.seconds//3600,
                "minutes": duration.seconds//60%60
                }
    
    payload["present"] = present

    ongoing_duration = None
    if present:
        ongoing_duration = datetime.now() - records_in[-1][1]
        print(ongoing_duration)

        payload["ongoing"] = {
                "days": ongoing_duration.days,
                "hours": ongoing_duration.seconds//3600,
                "minutes": ongoing_duration.seconds//60%60
                }

    return make_response(jsonify(payload), 200)

@app.route('/stats/parkduration/entity', methods=['GET'])
def get_parkduration_entity():
    entity = request.args.get('entity', default=None)

    if entity is None:
        return make_response("BAD REQUEST", 400)

    # Get entity's plates
    plates = db.read(db_requests.GET_PLATES_FROM_ENTITY.format(entityId=str(entity)))

    # Remove duplicates
    plates = [p[0] for p in set(plates)]

    duration = timedelta(days=0)

    for plate in plates:
        records_in = db_flow.read(db_requests.GET_PLATE_IN_DATETIMES_RECORDS.format(plate=plate))
        records_out = db_flow.read(db_requests.GET_PLATE_OUT_DATETIMES_RECORDS.format(plate=plate))


        for i in range(min(len(records_in), len(records_out))):
            duration += records_out[i][1] - records_in[i][1]

    return make_response({"duration": {
                    "days": duration.days,
                    "hours": duration.seconds//3600,
                    "minutes": duration.seconds/60%60
                }
            }, 200)
"""
@app.route('/admin/super/add', methods=['GET'])
def add_super_admin():
    req_data = dict(request.args)
    print(req_data)
    r = api.post_api(apiUrls.POST_USER, payload={
        "firstname": str(req_data['fname']),
        "lastname": str(req_data['lname']),
        "email": str(req_data['mail']),
        "license_plates": [],
        "contracts": [api.contract['_id']],
        "user_groups": [],
        "hierarchical_level": 3,
        "has_unlimited_geographical_access": True
    })

    if r.status_code != 200:
        return make_response(f"API ERROR:{r.text}", 500)

    try:
        profileId = db.read(db_requests.GET_PROFILE_ID_BY_NAME.format(
            name=req_data['profiles']))[0][0]
    except (IndexError, KeyError):
        return make_response("Le profil est incorrect", 400)

    pswdHash, salt = Auth.hash_password(req_data['pswd'])

    db.write(db_requests.INSERT_SUPER_ADMIN_USER.format(
        id=r.json()['_id'],
        firstname=str(req_data['fname']),
        lastname=str(req_data['lname']),
        mail=str(req_data['mail']),
        phone=str(req_data['phone']),
        usrType=profileId,
        entityId=str(req_data['entity'])))

    db.write(db_requests.INSERT_USER_CREDENTIALS.format(
        id=r.json()['_id'], login=req_data['login'], pswdHash=pswdHash, salt=salt))

    return make_response("CREATED", 201)
"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
