#!/usr/bin/env python3

import json
import requests
from random import randint

IPS_URI = 'http://178.128.55.51/ips/'
TIMEOUT = 5

class LinkGenerator:
    def get_random_link(self):
        with open("clean.names") as f:
            lines = f.readlines()

        uris = requests.get(IPS_URI).json()
        ip = uris[randint(0, len(uris) - 1)]

        rnd = randint(0, len(lines) - 1)
        name = lines[rnd].rstrip()
        return (f"http://{ip}/{name}", name)
