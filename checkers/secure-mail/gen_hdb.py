#!/usr/bin/env python3

import hashlib
import os
import uuid
import random
import base64

with open("../../services/secure-mail/clamav/db.hdb", "a") as hashes, open("malicious_content", "a") as malicious:
    i = 0
    while i < 5000:
        data = bytearray(random.randbytes(random.randint(100, 1024)))
        md5 = hashlib.md5(data).hexdigest()
        encoded = base64.b64encode(data).decode()
        hashes.write(f"{md5}:{len(data)}:{uuid.uuid4()}\n")
        malicious.write(f"{encoded}\n")
        i += 1
