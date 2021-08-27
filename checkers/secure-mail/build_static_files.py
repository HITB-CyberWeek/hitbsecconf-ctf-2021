#!/usr/bin/env python3

import sys
import base64
import os

if len(sys.argv) != 3:
    print(f"USAGE: {sys.argv[0]} <clean|malicious> <output dir>", file=sys.stderr)
    sys.exit(-1)

data_file_name = f"{sys.argv[1]}.data"
names_file_name = f"{sys.argv[1]}.names"

with open(data_file_name) as data, open(names_file_name) as names:
    i = 0
    while i < 5000:
        d = base64.b64decode(data.readline().rstrip())
        n = names.readline().rstrip()

        with open(os.path.join(sys.argv[2], n), "wb") as f:
            f.write(d)

        i += 1
