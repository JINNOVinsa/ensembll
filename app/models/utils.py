# coding: utf-8

from hashlib import sha256

from random import choice

from datetime import datetime, timedelta

try:
    import models.database.queries as db_requests
    from models.api import apiUrls
except:
    import database.queries as db_requests
    from api import apiUrls

class Auth:

    def hash_password(password):
        string_set = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&()*+,-./:;<=>?@[]^_{|}~"

        salt = ''.join([choice(string_set) for _ in range(15)])

        return sha256((password + salt).encode('utf-8')).hexdigest(), salt

    def check_password(user, hash_password, salt):
        return sha256((user + salt).encode('utf-8')).hexdigest() == hash_password

    def is_auth(token, db):
        if token is None:
            return None
        
        usr = db.read(db_requests.GET_USER_ID_FROM_TOKEN.format(token=token))
        if len(usr) == 0:
            return None
        
        return usr[0][0]
    
    def is_admin(usr_id, db):
        if usr_id is None:
            return False
        
        if db.read(db_requests.GET_USER_HIERARCHICAL_LEVEL.format(usrId=usr_id))[0][0] == 1:
            return True
        return False
    
    def is_super_admin(usr_id, db):
        if usr_id is None:
            return False
        
        if db.read(db_requests.GET_USER_HIERARCHICAL_LEVEL.format(usrId=usr_id))[0][0] == 2:
            return True
        
        return False
    
class Book:
    def gen_book_id(usrId, start, end):
        return Auth.hash_password(usrId + start + end)[0]

    def count_hovering(db, entity, booking_start, booking_end):
        return db.read(db_requests.GET_BOOKING_COUNT_FROM_ENTITY_OVERLAPPING_DATETIME.format(bookingStart=booking_start, bookingEnd=booking_end, entityId=entity))[0][0]
    
    def book(api, db, usrId, plate, start, end, interval, ending, customInterval=None, customAmount=None, repeatMonday=None, repeatTuesday=None, repeatWednesday=None, repeatThursday=None, repeatFriday=None, repeatSaturday=None, repeatSunday=None, bypass=False):
        bid = Book.gen_book_id(usrId, start, end)

        entity = db.read(db_requests.GET_ENTITY_ID_FROM_USER.format(usrId=usrId))[0][0]
        
        entity_total_spots = db.read(db_requests.GET_ENTITY_SPOTS.format(entityId=entity))[0][0]

        # Compute booking criticity
        usr_profile = db.read(db_requests.GET_USER_PROFILE.format(id=usrId))[0][0]
        profile_criticity = db.read(db_requests.GET_PROFILE_CRITICITY.format(profileId=usr_profile))[0][0]

        if start[8:10] != end[8:10]:
            time_criticity = max([l[0] for l in db.read(db_requests.GET_TIME_SLOTS_LEVELS_FOR_DATETIME.format(profileId=usr_profile, start="00:00:00.000000", end=end))] + [l[0] for l in db.read(db_requests.GET_TIME_SLOTS_LEVELS_FOR_DATETIME.format(profileId=usr_profile, start=start, end="23:59:59.000000"))], default=1)
        else:
            time_criticity = max([l[0] for l in db.read(db_requests.GET_TIME_SLOTS_LEVELS_FOR_DATETIME.format(profileId=usr_profile, start=start, end=end))], default=1)

        booking_criticity = profile_criticity * time_criticity

        if entity_total_spots > Book.count_hovering(db, entity, start, end) or bypass:
            # Classic booking
            if interval == "custom":
                db.write(db_requests.INSERT_CUSTOM_BOOKING.format(uuid=bid,
                                                                usrId=usrId,
                                                                plate=plate,
                                                                startTS=start,
                                                                endTS=end,
                                                                customInterval=customInterval,
                                                                customAmount=customAmount,
                                                                onMonday=repeatMonday,
                                                                onTuesday=repeatTuesday,
                                                                onWednesday=repeatWednesday,
                                                                onThursday=repeatThursday,
                                                                onFriday=repeatFriday,
                                                                onSaturday=repeatSaturday,
                                                                onSunday=repeatSunday,
                                                                criticity=booking_criticity,
                                                                ending=ending))
            else:
                db.write(db_requests.INSERT_BOOKING.format(uuid=bid,
                                                        usrId=usrId,
                                                        plate=plate,
                                                        startTS=start,
                                                        endTS=end,
                                                        interval=interval,
                                                        ending=ending,
                                                        criticity=booking_criticity))
            return Book.postBookingToApi(api, db, bid, usrId, datetime.strptime(start, "%Y-%m-%d %H:%M:%S.000000"), datetime.strptime(end, "%Y-%m-%d %H:%M:%S.000000"))
        else:
            # Search for a booking to delete
            bookings = Book.getEntityBookingsOverDatetime(db, entity, start, end)

            f = False
            for b in bookings:
                if b["criticity"] < booking_criticity:
                    f = True
                    # Suppression des enregistrements dans BookingsApiPeriods avant de supprimer l'enregistrement principal
                    db.write("DELETE FROM BookingsApiPeriods WHERE bookingId = '{bookingId}'".format(bookingId=b["bookingID"]))
                    
                    db.write(db_requests.DELETE_BOOKING.format(bookingId=b["bookingID"], usrId=b["userId"]))
                    break

            if f:
                if interval == "custom":
                    db.write(db_requests.INSERT_CUSTOM_BOOKING.format(uuid=bid,
                                                                    usrId=usrId,
                                                                    plate=plate,
                                                                    startTS=start,
                                                                    endTS=end,
                                                                    customInterval=customInterval,
                                                                    customAmount=customAmount,
                                                                    onMonday=repeatMonday,
                                                                    onTuesday=repeatTuesday,
                                                                    onWednesday=repeatWednesday,
                                                                    onThursday=repeatThursday,
                                                                    onFriday=repeatFriday,
                                                                    onSaturday=repeatSaturday,
                                                                    onSunday=repeatSunday,
                                                                    criticity=booking_criticity))
                else:
                    db.write(db_requests.INSERT_BOOKING.format(uuid=bid,
                                                            usrId=usrId,
                                                            plate=plate,
                                                            startTS=start,
                                                            endTS=end,
                                                            interval=interval,
                                                            ending=ending,
                                                            criticity=booking_criticity))
                        
                return Book.postBookingToApi(api, db, bid, usrId, datetime.strptime(start, "%Y-%m-%d %H:%M:%S.000000"), datetime.strptime(end, "%Y-%m-%d %H:%M:%S.000000"))
            else:
                return (False, 'no spots')

    
    def getEntityBookingsOverDatetime(db, entity, start, end):
        bookings = db.read(db_requests.GET_BOOKING_FROM_ENTITY_ID_OVERLAPPING_DATETIME.format(entityId=entity, bookingStart=start, bookingEnd=end))
        
        entity_bookings = list()
        for b in bookings:
            entity_bookings.append({
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
                'userProfileId': b[23]
            })
        return entity_bookings
    
    def postBookingToApi(api, db, bid: str, usrId: str, start: datetime, end: datetime):
        # Get start of the week timestamp
        interval_start = start - timedelta(days=(start.isoweekday() - 1), hours=start.hour, minutes=start.minute)
        interval_end = interval_start + timedelta(days=7)

        period = {
            "from": int(interval_start.timestamp()),
            "to": int(interval_end.timestamp()),
            "periods": {
                0: [],
                1: [],
                2: [],
                3: [],
                4: [],
                5: [],
                6: [],
            },
            'accesses': [a['_id'] for a in api.get_api(apiUrls.GET_ACCESSES).json()['accesses']]
        }

        api_user = api.get_api(apiUrls.GET_USER_FROM_ID, path_parameters={'id': usrId}).json()

        if start.date() == end.date():
            period["periods"][start.isoweekday() % 7] = [n for n in range(start.hour, min(end.hour + 1, 24))]

            # Remove any occurrence of 24 in periods
            for day in period["periods"]:
                if 24 in period["periods"][day]:
                    period["periods"][day].remove(24)

            r = api.post_api(apiUrls.POST_PERIOD, payload=period)

            if r.status_code != 200:
                return (False, 'api post period failed')
            
            customized_periods = [p['_id'] for p in api_user['customized_periods']]
            customized_periods.append(r.json()['_id'])
            db.write(db_requests.INSERT_API_PERIOD.format(id=r.json()['_id'], bookingId=bid))
            
            r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usrId}, data_payload={'customized_periods': customized_periods, 'contracts': [api.contract['_id']]})
            if r.status_code != 200:
                return (False, 'api update user failed')
        else:
            period["periods"][start.isoweekday() % 7] = [n for n in range(start.hour, 24)]

            right_limit = min(7 - start.isoweekday() % 7, (end - start).days)
            for i in range(1, right_limit + 1):
                period["periods"][(start.isoweekday() % 7 + i) % 7] = [j for j in range(24)]
            
            if start.date() != end.date() and (end - start).days <= 7 - start.isoweekday() % 7:
                period["periods"][(start.isoweekday() % 7 + (end - start).days) % 7] = [i for i in range(min(end.hour + 1, 24))]

                # Remove any occurrence of 24 in periods
                for day in period["periods"]:
                    if 24 in period["periods"][day]:
                        period["periods"][day].remove(24)

                r = api.post_api(apiUrls.POST_PERIOD, payload=period)
                if r.status_code != 200:
                    return (False, 'api post period failed')

                customized_periods = [p['_id'] for p in api_user['customized_periods']]
                customized_periods.append(r.json()['_id'])
                
                db.write(db_requests.INSERT_API_PERIOD.format(id=r.json()['_id'], bookingId=bid))
                r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usrId}, data_payload={'customized_periods': customized_periods, 'contracts': [api.contract['_id']]})
                if r.status_code != 200:
                    return False
            elif start.date() != end.date() and (end - start).days > 7 - start.isoweekday() % 7:
                # Remove any occurrence of 24 in periods
                for day in period["periods"]:
                    if 24 in period["periods"][day]:
                        period["periods"][day].remove(24)

                r = api.post_api(apiUrls.POST_PERIOD, payload=period)
                if r.status_code != 200:
                    return False
                
                customized_periods = [p['_id'] for p in api_user['customized_periods']]
                customized_periods.append(r.json()['_id'])

                db.write(db_requests.INSERT_API_PERIOD.format(id=r.json()['_id'], bookingId=bid))
                r = api.put_api(apiUrls.PUT_USER, path_payload={'id': usrId}, data_payload={'customized_periods': customized_periods, 'contracts': [api.contract['_id']]})
                if r.status_code != 200:
                    return (False, 'api update user failed')

                # In case a booking takes more than 7 days we call back this function with new start
                Book.postBookingToApi(api, db, bid, usrId, interval_start + timedelta(days=7), end)

        return (True, 'api completed')


    
    def delete_booking_periods(db, booking_id):
        try:
            db.write(db_requests.DELETE_BOOKING_PERIODS.format(bId=booking_id))
        except Exception as e:
            print(f"Error deleting booking periods: {e}")
            return False, str(e)
        return True, None

    def delete_booking(api, db, booking_id, usr):
        # Supprimer les périodes associées à la réservation
        success, err = Book.delete_booking_periods(db, booking_id)
        if not success:
            return False, err
        
        # Supprimer la réservation elle-même
        try:
            db.write(db_requests.DELETE_BOOKING_API.format(bookingId=booking_id))
            db.write(db_requests.DELETE_BOOKING.format(bookingId=booking_id, usrId=usr))
        except Exception as e:
            print(f"Error deleting booking: {e}")
            return False, str(e)
        return True, None


    def delete_periods(api, db, bid):
        periods_id = db.read(db_requests.GET_BOOKING_PERIOD.format(bId=bid))

        for p in periods_id:
            api.delete_api(apiUrls.DELETE_PERIOD, path_payload={'id': p[0]})
        db.write(db_requests.DELETE_BOOKING_PERIODS.format(bId=bid))
            
    def refresh_bookings(api, db):
        print("[INFO] Started a booking refresh")
        # Get booking's ids we need to refresh
        daily_booking_ids = [l[0] for l in db.read(db_requests.GET_BOOKING_IDS_DAILY_REFRESH)]
        
        # Refresh the bookings
        db.write(db_requests.REFRESH_DAILY_BOOKINGS_START)
        db.write(db_requests.REFRESH_DAILY_BOOKINGS_END)

        for bid in daily_booking_ids:
            # Remove each period associated with booking
            Book.delete_periods(api, db, bid)

            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=bid))[0]
            Book.postBookingToApi(api, db, bid, usr, start, end)

        # Weekly bookings
        weekly_bookings_ids = [l[0] for l in db.read(db_requests.GET_BOOKING_IDS_WEEKLY_REFRESH)]

        # Refresh the bookings
        db.write(db_requests.REFRESH_WEEKLY_BOOKINGS_START)
        db.write(db_requests.REFRESH_WEEKLY_BOOKINGS_END)

        for bid in weekly_bookings_ids:
            # Remove each period associated with booking
            Book.delete_periods(api, db, bid)

            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=bid))[0]
            Book.postBookingToApi(api, db, bid, usr, start, end)

        # Monthly bookings
        monthly_bookings_ids = [l[0] for l in db.read(db_requests.GET_BOOKING_IDS_MONTHLY_REFRESH)]

        # Refresh the bookings
        db.write(db_requests.REFRESH_MONTHLY_BOOKINGS_START)
        db.write(db_requests.REFRESH_MONTHLY_BOOKINGS_END)

        for bid in monthly_bookings_ids:
            # Remove each period associated with booking
            Book.delete_periods(api, db, bid)

            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=bid))[0]
            Book.postBookingToApi(api, db, bid, usr, start, end)
            

        # Custom daily bookings
        custom_daily_bookings_ids = [l[0] for l in db.read(db_requests.GET_BOOKING_IDS_CUSTOM_DAILY_REFRESH)]

        db.write(db_requests.REFRESH_CUSTOM_DAILY_BOOKINGS_START)
        db.write(db_requests.REFRESH_CUSTOM_DAILY_BOOKINGS_END)

        for bid in custom_daily_bookings_ids:
            Book.delete_periods(api, db, bid)

            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=bid))[0]
            Book.postBookingToApi(api, db, bid, usr, start, end)

        
        # Custom monthly bookings
        custom_monthly_bookings_ids = [l[0] for l in db.read(db_requests.GET_BOOKING_IDS_CUSTOM_MONTHLY_REFRESH)]

        db.write(db_requests.REFRESH_CUSTOM_MONTHLY_BOOKINGS_START)
        db.write(db_requests.REFRESH_CUSTOM_MONTHLY_BOOKINGS_END)

        for bid in custom_monthly_bookings_ids:
            Book.delete_periods(api, db, bid)

            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=bid))[0]
            Book.postBookingToApi(api, db, bid, usr, start, end)


        # Custom weekly bookings
        custom_weekly_bookings = db.read(db_requests.GET_BOOKING_IDS_CUSTOM_WEEKLY_REFRESH)
        weekday = datetime.today().weekday()
        

        for booking in custom_weekly_bookings:
            uuid = booking[0]
            custom_amount = booking[1]
            _, previous_start, _ = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=uuid))[0]
            previous_weekday = previous_start.weekday()

            days_index = list(range(7))
            days_index = days_index[previous_weekday+1:] + days_index[:previous_weekday+1]

            Book.delete_periods(api, db, uuid)

            for day_index in days_index:
                # Skip all non refreshing days
                if booking[2+ day_index] != 1:
                    continue
                
                # Update for this day which is reach day's index - last booking weekday (as this script will be run everyday this will be in theory current weekday)
                day_interval = day_index - previous_start.weekday()
                if day_index <= weekday:
                    # Here it's next week so we need to add extra 7 days times the custom amount
                    day_interval += 7 * custom_amount

                db.write(db_requests.REFRESH_CUSTOM_WEEKLY_BOOKINGS_START.format(bid=uuid, dayInterval=day_interval))
                db.write(db_requests.REFRESH_CUSTOM_WEEKLY_BOOKINGS_END.format(bid=uuid, dayInterval=day_interval))
                break   # We refresh only to the next date

            # Once the refresh is done in the db we update the api
            usr, start, end = db.read(db_requests.GET_USER_START_END_BOOKING.format(bid=uuid))[0]
            Book.postBookingToApi(api, db, uuid, usr, start, end)

        print("[INFO] Ended a booking refresh")
        return

    def datetimeToLocale(dt: datetime):
        months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        dt_day = days[dt.weekday()]
        dt_month = months[dt.month-1]
        return f"{dt_day} {dt.day} {dt_month} {dt.year} {dt.hour}h {str(dt.minute).zfill(2)}m"

if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv
    from database.db_utils import DbInputStream
    from api.apiInterface import APIinterface

    load_dotenv()
    db = DbInputStream('mysql-app', 3306, getenv("DB_ID"), getenv("DB_PSWD"))
    api_log = getenv("API_PARKKI_LOG")
    api_token = getenv("API_PARKKI_TOKEN")

    api = APIinterface()
    api.read_tokens()

    contracts = api.get_api(apiUrls.GET_CONTRACTS).json()['contracts']
    for c in contracts:
        if c['name'] == 'Humanicité':
            api.contract = c
            break

    Book.refresh_bookings(api, db)
