#!/usr/bin/env python3

import json
from random import randint

IPS_URI = 'http://178.128.55.51/ips/'
TIMEOUT = 5

class LinkGenerator:
    def get_random_link(self):
        with open("clean.names") as f:
            lines = f.readlines()

        rnd = randint(0, len(lines) - 1)
        name = lines[rnd].rstrip()
        return (f"http://10.60.56.129/{name}", name)
