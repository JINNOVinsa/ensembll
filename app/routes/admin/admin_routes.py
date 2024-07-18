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

from models.utils import Auth, Book
from flask import Flask, render_template, request, make_response, url_for, redirect, jsonify, Blueprint
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


load_dotenv()
db = DbInputStream('mysql-app', int(getenv("DB_PORT")), getenv("DB_ID"), getenv("DB_PSWD"))
db_flow = DbInputStream('mysql-flow', int(getenv("DB_PORT2")), getenv("DB_FLOW_ID"), getenv("DB_FLOW_PSWD"), database=getenv("DB_FLOW_NAME"))

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


admin_bp = Blueprint('admin', __name__, url_prefix='/adminPannel')

@admin_bp.route('/', methods=['GET'])
# @app.route('/adminPannel', methods=['GET'])
def adminPannel():
    return redirect(url_for('admin.adminPannelUsers'))

@admin_bp.route('/users', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/confirm', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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


@admin_bp.route('/bookings', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/fetchUserPlates', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/getUser', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/getAllUsers', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/getAllBookings', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/confirmUser', methods=['POST'])
# @app.route('/adminPannel/', methods=['POST'])
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

@admin_bp.route('/editUser', methods=['PUT'])
# @app.route('/adminPannel/', methods=['PUT'])
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

@admin_bp.route('/deleteUser', methods=['POST'])
# @app.route('/adminPannel/', methods=['POST'])
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

@admin_bp.route('/exportUsers', methods=['GET'])
# @app.route('/adminPannel/', methods=['GET'])
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

@admin_bp.route('/addProfile', methods=['POST'])
# @app.route('/adminPannel/', methods=['POST'])
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

@admin_bp.route('/editProfile', methods=['PUT'])
# @app.route('/adminPannel/', methods=['PUT'])
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

@admin_bp.route('/deleteProfile', methods=['DELETE'])
# @app.route('/adminPannel/deleteProfile', methods=['DELETE'])
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


@admin_bp.route('/newaccount', methods=['POST'])
# @app.route('/adminPannel/', methods=['POST'])
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


@admin_bp.route('/addUserBooking', methods=['POST'])
# @app.route('/adminPannel/', methods=['POST'])
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


@admin_bp.route('/deleteUserBooking', methods=['DELETE'])
# @app.route("/adminPannel/", methods=["DELETE"])
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