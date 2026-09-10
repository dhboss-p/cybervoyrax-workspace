import time
import mysql.connector
from flask import current_app

class Database:
    def __init__(self):
        self.app = None

    def init_app(self, app):
        self.app = app

    def _connection_kwargs(self):
        return {
            "host": current_app.config["MYSQL_HOST"],
            "port": current_app.config["MYSQL_PORT"],
            "database": current_app.config["MYSQL_DATABASE"],
            "user": current_app.config["MYSQL_USER"],
            "password": current_app.config["MYSQL_PASSWORD"],
            "autocommit": True,
        }

    def connect(self):
        return mysql.connector.connect(**self._connection_kwargs())

    def ping(self):
        try:
            conn = self.connect()
            conn.ping(reconnect=True, attempts=1, delay=0)
            conn.close()
            return True
        except mysql.connector.Error:
            return False

    def wait_until_ready(self):
        retries = current_app.config["DB_CONNECT_RETRIES"]
        delay = current_app.config["DB_CONNECT_RETRY_DELAY"]
        for _ in range(retries):
            if self.ping():
                return True
            time.sleep(delay)
        return False

    def fetch_one(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, params or ())
            return cur.fetchone()
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, params or ())
            return cur.fetchall()
        finally:
            conn.close()

    def execute(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
            return cur.lastrowid, cur.rowcount
        finally:
            conn.close()
