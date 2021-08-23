#!/usr/bin/env python3

import os
import sqlite3
import sys
import uuid
from dataclasses import dataclass

def trace(public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)

@dataclass
class User:
    name: str
    password: str

class UserDb:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'users.db')
        if not os.path.exists(db_path):
            trace("SQLite db file '%s' does not exist, creating" % db_path)
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('CREATE TABLE users (id VARCHAR PRIMARY KEY NOT NULL, host VARCHAR NOT NULL, username VARCHAR NOT NULL, password VARCHAR NOT NULL, created INT NOT NULL)')
            conn.commit()
            conn.close()
            trace("SQLite db file '%s' created" % db_path)

    def __enter__(self):
        db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'users.db')
        self.connection = sqlite3.connect(db_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def create_user(self, host, user_id):
        username = str(uuid.uuid4())
        password = str(uuid.uuid4())

        trace("Creating user for id '%s'" % user_id)
        cur = self.connection.cursor()
        cur.execute("INSERT INTO users VALUES (?,?,?,?,strftime('%s','now'))", (user_id, host, username, password))
        self.connection.commit()
        trace("User for id '%s' created" % user_id)

        return User(username, password)
