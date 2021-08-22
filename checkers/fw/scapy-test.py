#!/usr/bin/env python3
import random
import sys
from scapy.config import conf
conf.ipv6_enabled = False
from scapy.all import *

ans = sr1(IP(dst="172.17.0.2", options=IPOption(b'\x30\x06\x11\x22\x33\x44'))/UDP(sport=random.randrange(1024,65535), dport=17777)/("GET " + sys.argv[1]))
x = ans[0][0][0]
flag = bytes(x[UDP].payload).decode()
print("Response:", flag)
# print(ans_ip)
