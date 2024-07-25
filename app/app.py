# coding: utf-8
import logging
from loaders import RecursiveFileSystemLoader
from static.assets.usr import profilesTypes as img

from models.api import apiUrls
from models.utils import Auth, Book
from models.mailling.mailInterface import Mailling
import models.mailling.mailPayloads as mails
import models.database.queries as db_requests
import re

from flask import Flask, render_template, request, make_response, url_for, redirect, jsonify
from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

from mysql.connector.errors import IntegrityError

from re import match
from uuid import uuid4
from config import Config

BASE_APP_URL = "https://cogestion-parking.ensembll.fr"

imagePath = "static/assets/park7_logo.png"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        from routes.admin.admin_routes import admin_bp
        from routes.superAdmin.super_admin_routes import super_admin_bp
        from routes.stats.stats_routes import stats_bp

        app.register_blueprint(admin_bp)
        app.register_blueprint(super_admin_bp)
        app.register_blueprint(stats_bp)
    return app
app = create_app()

app.jinja_loader = RecursiveFileSystemLoader('templates')

db = app.config['DB_APP']
db_flow = app.config['DB_FLOW']
mail_host = app.config['MAIL_HOST']
mail_pswd = app.config['MAIL_PSWD']
api = app.config['API']
contract = app.config['CONTRACT']
capacity = app.config['CAPACITY']
parked_cars = app.config['PARKED_CARS']
statsApi = app.config['STATS_API']
area_id = app.config['AREA_ID']



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
        # logging.basicConfig(level=logging.DEBUG)
        # logging.debug("Boo ------------------------------------------")
        # logging.debug(b[4])
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

@app.route('/get_profiles_by_entity', methods=['GET'])
def get_profiles_by_entity():
    entity_id = request.args.get('entityId')
    profiles = db.read(db_requests.GET_PROFILES_BY_ENTITY.format(entityId=entity_id))
    return jsonify(profiles)

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
    
    payload = {
    "firstname": str(req_data['fname']),
    "lastname": str(req_data['lname']),
    "email": str(req_data['mail']),
    "license_plates": [req_data['plate']],
    "contracts": [api.contract['_id']],
    "user_groups": [],
    "hierarchical_level": 3,
    "has_unlimited_geographical_access": True
    }

    # Envoi de la requête POST
    r = api.post_api(apiUrls.POST_USER, payload=payload)
    
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
        response_json = r.json()
        description = response_json.get("description", "No description available")
        return make_response(f"API ERROR, {description}", 400)
  
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
        "phone": ' '.join([str(user[3])[i:i+2] for i in range(0, len(str(user[3])), 2)]) if user[3] is not None else "none",
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)