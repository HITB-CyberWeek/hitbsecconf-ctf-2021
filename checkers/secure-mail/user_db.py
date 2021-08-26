#!/usr/bin/env python3

import uuid
import json
import base64
from dataclasses import dataclass
from checker_helper import *

@dataclass
class User:
    name: str
    password: str

class UserDb:
    def create_user(self, host, user_id):
        username = str(uuid.uuid4())
        password = str(uuid.uuid4())
        return User(username, password)

    def read_user(self, host, flag_id):
        try:
            name, password = json.loads(base64.b64decode(flag_id))
        except Exception as e:
            verdict(CHECKER_ERROR, "Can't read user from encoded flag_id: %s" % str(e))
        return User(name, password)
