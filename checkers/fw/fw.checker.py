#!/usr/bin/env python3
import hashlib
import hmac
import logging
import os

import base64
import random
import socket
import string
import sys
import time

from scapy.all import *

FLAG_PORT = 17777
FW_PORT = 17778
SOCKET_TIMEOUT = 3
RETRY_DELAY = 0.3
RETRY_COUNT = 3
ENCODING = "utf-8"

ID_LEN = 14  # cf5j-dxa9-6gpx
PASSWORD_LEN = 24

LOGS_DIR = "logs"

HMAC_PASS_KEY = "9d5c73ef85594d_39da23463fd"


class Client:
    def __init__(self, host):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(SOCKET_TIMEOUT)
        self.sock = sock
        self.host = host

    def talk(self, port: int, data: str, wait_response=True):
        try_number = 1
        while True:
            logging.debug("[ =>] Send: %r to port %d (try %d)", data, port, try_number)
            self._send(port, data)
            if not wait_response:
                return None
            logging.debug("Waiting for reponse ...")
            try:
                data = self._recv()
                logging.debug("[<= ] Recv: %r", data)
                return data
            except socket.timeout:
                if try_number >= RETRY_COUNT:
                    raise
                logging.debug("No answer, retrying")
                time.sleep(RETRY_DELAY)
            try_number += 1

    def _send(self, port: int, data: str):
        data_bytes = bytes(data, ENCODING)
        self.sock.sendto(data_bytes, (self.host, port))

    def _recv(self):
        data_bytes = self.sock.recv(65536)
        return data_bytes.decode(ENCODING)


class ExitCode:
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    FAIL = 104
    INTERNAL_ERROR = 110


def fail_on_timeout(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.timeout:
            logging.error("Timed out after all retries.")
            return ExitCode.FAIL
    return wrapper


def create_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def create_password(flag_id):
    pass_bytes = hmac.new(HMAC_PASS_KEY.encode(), msg=flag_id.encode(), digestmod=hashlib.md5).digest()
    return base64.b64encode(pass_bytes).decode()


@fail_on_timeout
def check(ip):
    client = Client(ip)

    response = client.talk(FLAG_PORT, "PIN")
    if response == "PON":
        return ExitCode.OK

    return ExitCode.MUMBLE


@fail_on_timeout
def put(ip, id, flag, *args):
    if len(id) != ID_LEN:
        raise Exception("Bad flag ID length: {}, should be {}.".format(len(id), ID_LEN))
    # id = create_random_string(ID_LEN)
    password = create_password(id)
    logging.debug("Generated password: %r", password)
    if len(password) != PASSWORD_LEN:
        raise Exception("Password generation bug.")

    client = Client(ip)
    response = client.talk(FLAG_PORT, "PUT {} {}".format(id, flag))
    if response != "OK":
        return ExitCode.MUMBLE
    response = client.talk(FW_PORT, "LCK {} {}".format(id, password))
    if response != "OK":
        return ExitCode.MUMBLE

    return ExitCode.OK


@fail_on_timeout
def get(ip, id, flag, *args):
    client = Client(ip)

    response = client.talk(FLAG_PORT, "DIR")
    if id not in response:
        logging.error("Flag ID (%r) wasn't found in DIR response.", id)
        return ExitCode.CORRUPT

    response = client.talk(FLAG_PORT, "GET {}".format(id))  # FIXME: add PASS to IP options!
    if response != flag:
        logging.error("Wrong flag data received.")
        return ExitCode.CORRUPT

    return ExitCode.OK


def configure_logging(ip):
    log_format = "%(asctime)s %(levelname)-8s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format, stream=sys.stderr)


def main():
    if len(sys.argv) < 3:
        print("Usage: {} (check|put|get) IP".format(sys.argv[0]))
        sys.exit(ExitCode.INTERNAL_ERROR)

    mode = sys.argv[1]
    args = sys.argv[2:]

    configure_logging(ip=sys.argv[2])
    logging.info("Started with arguments: %r", sys.argv)

    if mode == "check":
        exit_code = check(*args)
    elif mode == "put":
        exit_code = put(*args)
    elif mode == "get":
        exit_code = get(*args)
    else:
        exit_code = ExitCode.INTERNAL_ERROR
        logging.error("Unknown mode.")

    logging.info("Exiting with code %d", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
