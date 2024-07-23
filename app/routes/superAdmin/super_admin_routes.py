from models.api import apiUrls
from models.api import statsUrls
from models.utils import Auth, Book
from models.mailling.mailInterface import Mailling
import models.mailling.mailPayloads as mails
import models.database.queries as db_requests

from models.utils import Auth, Book
from flask import current_app, render_template, request, make_response, url_for, redirect, jsonify, Blueprint
from datetime import datetime
import locale

from decorators import role_required

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

from re import match

from io import StringIO
import csv

imagePath = "static/assets/park7_logo.png"


db = current_app.config['DB_APP']
db_flow = current_app.config['DB_FLOW']
mail_host = current_app.config['MAIL_HOST']
mail_pswd = current_app.config['MAIL_PSWD']
api = current_app.config['API']
contract = current_app.config['CONTRACT']
capacity = current_app.config['CAPACITY']
parked_cars = current_app.config['PARKED_CARS']
statsApi = current_app.config['STATS_API']
area_id = current_app.config['AREA_ID']

super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/superAdminPannel')

@super_admin_bp.route('/profiles', methods=['GET'])
@role_required("super_admin")
def superAdminPannelProfiles():
    auth_token = request.cookies.get('SESSID', default=None)
    usr_id = Auth.is_auth(auth_token, db)

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

@super_admin_bp.route('/timeslots', methods=['GET'])
@role_required("super_admin")
def superAdminPannelProfilfesTimeSlots():
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

@super_admin_bp.route('/addtimeslots', methods=['POST'])
@role_required("super_admin")
def superAdminPannelAddTimeSlot():
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

@super_admin_bp.route('/deletetimeslot', methods=['POST'])
@role_required("super_admin")
def superAdminPannelDeleteTimeSlot():
    token = request.cookies.get("SESSID", default=None)

    super_admin_id = Auth.is_auth(token, db)

    time_slot_id = request.form.get("timeslot", default=None)

    if time_slot_id is None:
        return make_response("BAD REQUEST", 400)
 
    admin_entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=super_admin_id))[0][0]
    time_slot = db.read(db_requests.GET_TIME_SLOT_BY_ID.format(id=time_slot_id))

    try:
        time_slot = time_slot[0]
    except:
        return make_response("NOT FOUND", 404)
    
    db.write(db_requests.DELETE_TIME_SLOT.format(id=time_slot_id))

    return make_response("OK", 200)


@super_admin_bp.route('/users', methods=['GET'])
@role_required("super_admin")
def superAdminPannelUsers():
    users_count = db.read(db_requests.GET_USERS_AND_ADMIN_COUNT)[0][0]
    entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)
    profiles = db.read(db_requests.GET_PROFILES)

    return render_template('super-admin-pannel-users.html', connected=True, usercount=users_count, entities=entities, profiles=profiles)

@super_admin_bp.route('/', methods=['GET'])
@role_required("super_admin")
def superAdminPannel():
    return redirect(url_for('super_admin.superAdminPannelUsers'))


@super_admin_bp.route('/confirm', methods=['GET'])
@role_required("super_admin")
def superAdminPannelConfirm():
    user_count = db.read(db_requests.GET_USERS_TO_CONFIRM_COUNT)[0][0]
    pNames = [p[0] for p in db.read(db_requests.GET_PROFILES_NAMES)]
    entities = db.read(db_requests.GET_ALL_ENTITIES_IDS_AND_NAMES)

    return render_template('super-admin-pannel-confirm.html', connected=True, usercount=user_count, profilesNames=pNames, entities=entities)

@super_admin_bp.route('/allocation', methods=['GET'])
@role_required("super_admin")
def superAdminPannelAllocation():
    token = request.cookies.get('SESSID', default=None)

    super_admin_id = Auth.is_auth(token, db)
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
    userHierarchy = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=super_admin_id))[0]

    return render_template('super-admin-pannel-allocation.html', connected=True, total_spots=spots, entry=entities, nbFreePlaces=nbFreePlaces, userHierarchy=userHierarchy)

@super_admin_bp.route('/bookings', methods=['GET'])
@role_required("super_admin")
def superAdminPannelBookings():
    bookings_count = db.read(db_requests.GET_CURRENT_BOOKINGS_COUNT)[0][0]

    return render_template('super-admin-pannel-bookings.html', connected=True, bookingcount=bookings_count)


@super_admin_bp.route('/editAllocation', methods=['PUT'])
@role_required("super_admin")
def editAllocation():
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

@super_admin_bp.route('/getAllUsersAndAdmin', methods=['GET'])
@role_required("super_admin")
def getAllUsersAndAdmin():
    auth_token = request.cookies.get("SESSID", default=None)
    super_admin_id = Auth.is_auth(auth_token, db)
    
    try:
        db.read(db_requests.GET_USER_RGPD.format(usrId=super_admin_id))[0][0]
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

@super_admin_bp.route('/editUser', methods=['PUT'])
@role_required("super_admin")
def superEditUser():
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

@super_admin_bp.route('/confirmUser', methods=['POST'])
@role_required("super_admin")
def superConfirmUser():
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

@super_admin_bp.route('/deleteUser', methods=['POST'])
@role_required("super_admin")
def superDeleteUser():
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

@super_admin_bp.route('/exportUsers', methods=['GET'])
@role_required("super_admin")
def superAdminExportUsers():
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

@super_admin_bp.route('/getAllBookings', methods=['GET'])
@role_required("super_admin")
def superGetAllBookingsFromEntity():
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

@super_admin_bp.route('/getAllUsers', methods=['GET'])
@role_required("super_admin")
def getAllUsers():
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

@super_admin_bp.route('/fetchUserPlates', methods=['GET'])
@role_required("super_admin")
def superAdminPannelUserPlates():
    user_id = request.args.get('usrID', default=None)

    if user_id is None:
        return make_response('BAD REQUEST', 400)
    
    plates = db.read(db_requests.GET_USER_PLATES.format(usrId=user_id))
    return make_response(plates, 200)


@super_admin_bp.route('/newaccount', methods=['POST'])
@role_required("super_admin")
def superAdminSubmitAccount():
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

@super_admin_bp.route('/newadminaccount', methods=['POST'])
@role_required("super_admin")
def superAdminSubmitAdminAccount():
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


@super_admin_bp.route('/allocation/addEntity', methods=['POST'])
@role_required("super_admin")
def superAdminAddEntity():
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

@super_admin_bp.route('/allocation/deleteEntity', methods=['POST'])
@role_required("super_admin")
def superAdminDeleteEntity():
    entity_id = request.form.get('id', default=None)

    if entity_id is None:
        return make_response("BAD REQUEST", 400)

    db.write(db_requests.DELETE_ENTITY.format(id=entity_id))

    return make_response("OK", 200)

@super_admin_bp.route('/getbooking', methods=['GET'])
@role_required("super_admin")
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

@super_admin_bp.route('/addUserBooking', methods=['POST'])
@role_required("super_admin")
def superAddUserBooking():

    # Récupérer les places disponibles sur la période de temps
    """
    
    PARTIE API:
        - Récupération disponibilité et retours à l'utilisateur
        - Vérification si périodicité est valide sur la période demandée (nécessite de changer la db et d'orienter les tables sur des plages de temps)
    
    """

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


@super_admin_bp.route('/deleteUserBooking', methods=['DELETE'])
@role_required("super_admin")
def superDeleteUserBooking():

    booking_id = request.form.get('id')
    usr_id = request.form.get('usrId')

    if booking_id is None or usr_id is None:
        return make_response('BAD REQUEST', 400)
    
    Book.delete_booking(api, db, booking_id, usr_id)
    return make_response('DELETE SUCCESSFULL', 200)