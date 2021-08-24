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


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

PASSMAN_PORT = 3255
TIMEOUT = 5

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
UNPRINTABLES = "\x00\x01\x02\x03"

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
            break
        pkt_fields.append(pkt_rest[1:1+pkt_fields_len])
        pkt_rest = pkt_rest[1+pkt_fields_len:]
    return tuple(pkt_fields)

def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)


def info():
    verdict(OK, "vulns: 1")


def register_user(s, login, password):
    send_raw_pkt(s, gen_cmd_pkt(CMD_REGISTER, login, password))
    get_and_parse_cmd_pkt(s)


def login_user(s, login, password):
    send_raw_pkt(s, gen_cmd_pkt(CMD_START_LOGIN, login))
    challenge = get_and_parse_cmd_pkt(s, expected_type=ANS_CHALLENGE)[0]

    AES_BLOCK_LENGTH = 16
    aes_key = (password.encode() + b"\x00"*AES_BLOCK_LENGTH)[:AES_BLOCK_LENGTH]

    cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), default_backend())
    decryptor = cipher.decryptor()

    challenge_ans = decryptor.update(challenge)[:4]

    send_raw_pkt(s, gen_cmd_pkt(CMD_ANS_LOGIN_CHALL, challenge_ans))
    get_and_parse_cmd_pkt(s)


def put_pass(s, index, pass_desc, password):
    send_raw_pkt(s, gen_cmd_pkt(CMD_PUT_PASS, bytes([index]), pass_desc, password))
    get_and_parse_cmd_pkt(s)


def get_pass_name(s, index):
    send_raw_pkt(s, gen_cmd_pkt(CMD_GET_PASS_NAME, bytes([index])))
    password_desc = get_and_parse_cmd_pkt(s, expected_type=ANS_PASS_NAME_INFO)[0]
    return password_desc

def get_pass(s, index):
    send_raw_pkt(s, gen_cmd_pkt(CMD_GET_PASS, bytes([index])))
    password = get_and_parse_cmd_pkt(s, expected_type=ANS_PASS_INFO)[0]
    return password


def user_is_in_list(s, user):
    PER_PAGE = 100
    MAX_PAGES = 10

    if hasattr(user, "encode"):
        user = user.encode()

    for page in range(MAX_PAGES):
        for u in range(PER_PAGE):
            user_as_bytes = int.to_bytes(page*PER_PAGE+u, 4, "big")
            send_raw_pkt(s, gen_cmd_pkt(CMD_GET_NAME, user_as_bytes))
        found = False
        for u in range(PER_PAGE):
            user_info = get_and_parse_cmd_pkt(s, expected_type=None)
            if len(user_info) == 1 and user_info[0] == user:
                found = True
        if found:
            return True
    return False


def check(host):
    try:
        s = socket.create_connection((host, PASSMAN_PORT), timeout=TIMEOUT)
    except Exception as E:
        verdict(DOWN, "connect failed", "connect failed: %s" % E)


    login = gen_random_string(8, 100)
    password = gen_random_string(8, 100)

    login2 = gen_random_string(8, 12)
    password2 = gen_random_string(8, 12)

    try:
        register_user(s, login, password)
        register_user(s, login2, password2)
        login_user(s, login, password)

        desc1 = gen_random_string(1, 10)
        pass1 = gen_random_string(1, 10)

        desc2 = gen_random_string(80, 100)
        pass2 = gen_random_string(80, 100)

        put_pass(s, 1, desc1, pass1)
        put_pass(s, 2, desc2, pass2)

        if get_pass_name(s, 2) != desc2.encode():
            verdict(MUMBLE, "failed to store pass name", "different infos, test 1")
        if get_pass(s, 2) != pass2.encode():
            verdict(MUMBLE, "failed to store pass", "different passes, test 1")

        login_user(s, login2, password2)

        desc3 = gen_random_string(10, 20, abc=UNPRINTABLES)
        pass3 = gen_random_string(10, 20, abc=UNPRINTABLES)

        put_pass(s, 1, desc3, pass3)
        if get_pass_name(s, 1) != desc3.encode():
            verdict(MUMBLE, "failed to store pass name", "different infos, test 2")
        if get_pass(s, 1) != pass3.encode():
            verdict(MUMBLE, "failed to store pass", "different passes, test 2")

        login_user(s, login, password)

        if get_pass_name(s, 1) != desc1.encode():
            verdict(MUMBLE, "failed to store pass name", "different infos, test 3")
        if get_pass(s, 1) != pass1.encode():
            verdict(MUMBLE, "failed to store pass", "different passes, test 3")

        if not user_is_in_list(s, login2):
            verdict(MUMBLE, "bad users list", "no user 2 found")

        if not user_is_in_list(s, login):
            verdict(MUMBLE, "bad users list", "no user 1 found")

    except Exception as E:
        verdict(MUMBLE, "unexpected answer", "unexpected answer: %s" % E)

    verdict(OK)


def put(host, flag_id, flag, vuln):
    try:
        s = socket.create_connection((host, PASSMAN_PORT), timeout=TIMEOUT)
    except Exception as E:
        verdict(DOWN, "connect failed", "connect failed: %s" % E)

    login = flag_id
    password = gen_random_string()
    desc = gen_random_string()

    try:
        register_user(s, flag_id, password)
        login_user(s, flag_id, password)
        put_pass(s, 1, desc, flag)
    except Exception as E:
        verdict(MUMBLE, "unexpected answer", "unexpected answer: %s" % E)

    flag_id = base64.b64encode(json.dumps([login, password, desc]).encode()).decode()
    verdict(OK, flag_id)


def get(host, flag_id, flag, vuln):
    try:
        login, password, desc = json.loads(base64.b64decode(flag_id))
    except Exception:
        verdict(CHECKER_ERROR, "Bad flag id", "Bad flag_id: %s" % traceback.format_exc())

    try:
        s = socket.create_connection((host, PASSMAN_PORT), timeout=TIMEOUT)
    except Exception as E:
        verdict(DOWN, "connect failed", "connect failed: %s" % E)

    try:
        if not user_is_in_list(s, login):
            verdict(CORRUPT, "no such user", "no such user")

        login_user(s, login, password)

        got_flag = get_pass(s, 1)
        if got_flag != flag.encode():
            verdict(CORRUPT, "no such flag", "no such flag")

    except Exception as E:
        verdict(MUMBLE, "unexpected answer", "unexpected answer: %s" % E)

    verdict(OK)


def main(args):
    CMD_MAPPING = {
        "info": (info, 0),
        "check": (check, 1),
        "put": (put, 4),
        "get": (get, 4),
    }

    if not args:
        verdict(CHECKER_ERROR, "No args", "No args")

    cmd, args = args[0], args[1:]
    if cmd not in CMD_MAPPING:
        verdict(CHECKER_ERROR, "Checker error", "Wrong command %s" % cmd)

    handler, args_count = CMD_MAPPING[cmd]
    if len(args) != args_count:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for %s" % cmd)

    try:
        handler(*args)
    except ConnectionError as E:
        verdict(DOWN, "Connect error", "Connect error: %s" % E)
    except socket.timeout as E:
        verdict(DOWN, "Timeout", "Timeout: %s" % E)
    except json.decoder.JSONDecodeError as E:
        verdict(MUMBLE, "Json decode error", "Json decode error: %s" % traceback.format_exc())
    except Exception as E:
        verdict(CHECKER_ERROR, "Checker error", "Checker error: %s" % traceback.format_exc())
    verdict(CHECKER_ERROR, "Checker error", "No verdict")


if __name__ == "__main__":
    main(args=sys.argv[1:])
