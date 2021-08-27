#!/usr/bin/env python3

import hashlib
import os
import uuid
import random
import base64

with open("../../services/secure-mail/clamav/db.hdb", "a") as hashes, open("malicious.data", "a") as malicious, open("malicious.names", "a") as mnames:
    i = 0
    while i < 5000:
        data = bytearray(random.randbytes(random.randint(100, 1024)))
        md5 = hashlib.md5(data).hexdigest()
        encoded = base64.b64encode(data).decode()
        name = uuid.uuid4()
        hashes.write(f"{md5}:{len(data)}:{name}\n")
        malicious.write(f"{encoded}\n")
        mnames.write(f"{name}\n")
        i += 1

with open("clean.data", "a") as clean, open("clean.names", "a") as cnames:
    i = 0
    while i < 5000:
        data = bytearray(random.randbytes(random.randint(100, 1024)))
        encoded = base64.b64encode(data).decode()
        clean.write(f"{encoded}\n")
        cnames.write(f"{uuid.uuid4()}\n")
        i += 1
