from dotenv import load_dotenv
from os import getenv

from models.api.apiInterface import APIinterface
from models.database.db_utils import DbInputStream

import models.database.queries as db_requests

from models.Objects.Entity import Entity
from models.Objects.User import User
from models.Objects.Booking import Booking
from models.Objects.Parking import Parking
from models.Objects.ExceptionalOpen import ExceptionalOpen


class SyncAPIdb:

    def __init__(self) -> None:
        load_dotenv()
        self.db = DbInputStream(
            'localhost', 3306, getenv("DB_ID"), getenv("DB_PSWD"))

    def fetch_db(self) -> dict:
        """Fetch stored data in local database

        Returns:
            dict: Data's dictionnary based on Objects models
        """

        data = {
            "entities": list(),
            "users": list(),
            "parkings": list()
        }

        # Fetch entities
        for e in self.db.read(db_requests.GET_ALL_ENTITIES):
            data["entities"].append(Entity(e[0], e[1], e[2]))

        # Fetch users
        for u in self.db.read(db_requests.GET_ALL_USERS_INFOS):

            # Fetch plates associated to current user
            plates = list()
            for p in self.db.read(db_requests.GET_USER_PLATES.format(usrId=u[0])):
                plates.append(p[0])

            # Fetch users' bookings
            bookings = list()
            for b in self.db.read(db_requests.GET_USER_BOOKINGS.format(usrId=u[0])):
                bookings.append(Booking(b[0], b[1], b[2], b[3], b[4]))

            data["users"].append(
                User(u[0], u[1], u[2], u[3], u[4], plates, u[5], bookings=bookings))

        # Fetch parkings
        for p in self.db.read(db_requests.GET_ALL_PARKINGS):

            # Fetch exceptionnal openings associated to parkings
            ex_opens = list()
            for ex_open in self.db.read(db_requests.GET_PARKING_EXCEPTIONAL_OPEN.format(pId=p[0])):
                ex_opens.append(ExceptionalOpen(
                    ex_open[0], ex_open[1], ex_open[2], ex_open[3]))

            data["parkings"].append(Parking(p[0], p[1], p[2], p[3], ex_opens))

        return data

    def close_db(self):
        """ Close database socket """
        self.db.close_conn()


if __name__ == "__main__":
    sync = SyncAPIdb()
    sync.fetch_db()
    print("All is fine")
    sync.close_db()
