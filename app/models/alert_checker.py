from database.db_utils import DbInputStream
import database.queries as db_requests

from datetime import datetime, timedelta

from dotenv import load_dotenv
from os import getenv

from utils import Auth
from time import sleep
load_dotenv()

TIME_DELTA = 8*60_000   # 8 minutes

db = DbInputStream("mysql-app", getenv("DB_PORT"), getenv("DB_ID"), getenv("DB_PSWD"))
db_flow = DbInputStream("mysql-flow", getenv("DB_PORT"), getenv("DB_FLOW_ID"), getenv("DB_FLOW_PSWD"), database=getenv("DB_FLOW_NAME"))

while True:
    print("[*] Start an alert checking")
    now = datetime.now()

    # Get new parking entries
    flow_in = db_flow.read(db_requests.GET_FLOW_IN_IN_INTERVAL.format(startTS=now-timedelta(milliseconds=TIME_DELTA), endTS=now))
    for record in flow_in:
        # Check if its in a booking
        booking = db.read(db_requests.GET_BOOKING_FOR_DATETIME_AND_PLATE.format(datetime=record[1], plate=record[0]))
        if len(booking) > 0:
            continue

        # Not in a booking
        # Check if its at least 15 minutes before next booking
        next_booking = db.read(db_requests.GET_BOOKINGS_STARTS_IN_INTERVAL.format(startInterval=record[1], endInterval=record[1]+timedelta(milliseconds=2*TIME_DELTA), plate=record[0]))
        if len(next_booking) > 0:
            continue

        # Check if he has a booking register in the next 24 hours
        day_booking = db.read(db_requests.GET_BOOKINGS_STARTS_IN_INTERVAL.format(startInterval=record[1], endInterval=record[1]+timedelta(hours=24), plate=record[0]))
        # Register an alert

        # Earlier = 1 - Present 15+ minutes before its booking
        # Earlier = 2 - Present without any booking

        aid = Auth.hash_password(record[0]+"-"+str(record[1].timestamp()))[0]
        if len(day_booking) < 1:
            db.write(db_requests.INSERT_ALERT_WITHOUT_BOOKING.format(id=aid, earlier=2, later=0, plate=record[0]))
        else:
            day_booking = day_booking[0]
            user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=day_booking[1]))[0]
            db.write(db_requests.INSERT_ALERT_WITH_BOOKING.format(id=aid, earlier=1, later=0, plate=record[0], firstName=user[0], lastName=user[1], start=day_booking[4], end=day_booking[5]))
            # Get parking exits
    flow_out = db_flow.read(db_requests.GET_FLOW_OUT_IN_INTERVAL.format(startTS=now-timedelta(milliseconds=TIME_DELTA), endTS=now))

    for record in flow_out:
        # Check if its in a booking
        booking = db.read(db_requests.GET_BOOKING_FOR_DATETIME_AND_PLATE.format(datetime=record[1], plate=record[0]))

        if len(booking) > 0:
            continue

        # Not in a booking
        # Check if its at least 15 minutes after previous
        previous_booking = db.read(db_requests.GET_BOOKINGS_ENDS_IN_INTERVAL.format(startInterval=record[1]-timedelta(milliseconds=2*TIME_DELTA), endInterval=record[1], plate=record[0]))

        if len(previous_booking) > 0:
            continue

        # Check if he has a booking register in the next 24 hours
        day_booking = db.read(db_requests.GET_BOOKINGS_STARTS_IN_INTERVAL.format(startInterval=record[1]-timedelta(hours=24), endInterval=record[1], plate=record[0]))
        # Register an alert

        # Later = 1 - Present 15+ minutes after its booking
        # Later = 2 - Present without any booking

        aid = Auth.hash_password(record[0]+"-"+str(record[1].timestamp()))[0]
        if len(day_booking) < 1:
            db.write(db_requests.INSERT_ALERT_WITHOUT_BOOKING.format(id=aid, earlier=0, later=2, plate=record[0]))
        else:
            day_booking = day_booking[0]
            user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=day_booking[1]))[0]
            db.write(db_requests.INSERT_ALERT_WITH_BOOKING.format(id=aid, earlier=0, later=1, plate=record[0], firstName=user[0], lastName=user[1], start=day_booking[4], end=day_booking[5]))

    # Check non-used bookings

    bookings = db.read(db_requests.GET_BOOKINGS_ENDS_IN_INTERVAL_WITHOUT_PLATE.format(startInterval=now-timedelta(milliseconds=2*TIME_DELTA), endInterval=now))
    for booking in bookings:
        # Check if the corresponding plate entered from the last 24h to booking's end and exited or still didnt exit by now

        plate_in = db_flow.read(db_requests.GET_PLATE_FLOW_IN_IN_INTERVAL.format(startTS=booking[4]-timedelta(hours=24), endTS=booking[5]-timedelta(minutes=1), plate=booking[2]))
        plate_out = db_flow.read(db_requests.GET_PLATE_FLOW_OUT_IN_INTERVAL.format(startTS=booking[4]-timedelta(hours=23, minutes=59), endTS=booking[5]-timedelta(minutes=1), plate=booking[2]))

        if len(plate_in) - len(plate_out) == 1:
            # Car is in the parking
            continue

        # Check if the last exit is during the booking
        # Only check starts because when we retreive plate_out, right side of the interval match booking end
        if len(plate_out) > 0 and plate_out[-1][1] > booking[4]:
            continue

        # Create an alert
        aid = Auth.hash_password(booking[0]+"-"+str(booking[4].timestamp()))[0]
        user = db.read(db_requests.GET_USER_INFO_BY_ID.format(id=booking[1]))[0]
        db.write(db_requests.INSERT_ALERT_WITH_BOOKING.format(id=aid, earlier=0, later=0, plate=booking[2], firstName=user[0], lastName=user[1], start=booking[4], end=booking[5]))

    print(f"[*] Sleep {2*TIME_DELTA}ms")
    sleep(2*TIME_DELTA /1000)
