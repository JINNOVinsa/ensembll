# coding: utf-8

from mysql.connector import connect

class DbInputStream:

    def __init__(self, host: str, port: int, user: str, pswd: str, database: str = "Ensembll") -> None:
        self.host = host
        self.port = port
        self.user = user
        self.pswd = pswd
        self.database = database

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

    def read(self, query: str) -> list:
        connection = self.connectToDb()
        csr = self.getCursor(connection)
        csr.execute(query)
        a = csr.fetchall()
        csr.close()
        self.disconnect(connection)
        return a

    def close_conn(self) -> None:
        self.connector.close()
