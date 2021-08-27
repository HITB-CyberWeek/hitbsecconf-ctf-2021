#!/usr/bin/env python3
import datetime
import hashlib
import hmac
import logging
import os
import random
import socket
import string
import sys
import time

from Crypto.PublicKey import RSA

n = 0xa337e14c4fa536382c3c290af8314a53d3be2025e1ad1343c2e017e9366f4e732007edc50eb280700ea877e2feace49a298c4f1734b93d4734bcb54b705848e458caaf24e6ce013d0db638a5c6c8c05675e452d868259c19710bbb7cdbe75f97ef4526e38a11a82ae4f33c2f1a37f672ed2ae6c12d8a06b722d3745abde383b1
e = 0x10001
d = 0x8c998b7bd8342283bb1f4bdfc63377aac48148623988854adee979cf8cf3cf297f133570861ba066674a1a9430fcb0a4585c249981f27c660578f5d7797ca3b4a70d36d70df15f1a2ac2d7efc827e1396d090d57aa62cf301c3ebb58c90f711406629d5a5db9f0196f3e0254823c8b89dd15c808757f0cc544df3368ea2d6401
p = 0xb8ce2a753fada33811db923a7d5946e924b58dab67ca6489cae5c0ff75334a5b8a18400d6e990c3ae841162a7e1223ceb5993b4d4dc7cd9fcb512aa5704bc971
q = 0xe218c29bf5ca5d36e33565c6971e7402e7202ac9bd951808537282b15d9d77e5b5c1b1130c17cd1290f86423b4a00c8e2ac6270980ff455b14c1f9928f9c3e41
u = 0x370ab0d379de905c413b42ce85038638f832ac3ffa099bf2b5ac5e8613cbed0e34b1f7840e7103b0ce55f85b88d3c7c77ef0aa66c6e3c708eaec2f887efaabb5
privkey = RSA.construct((n, e, d, p, q, u),)

from scapy.config import conf
conf.ipv6_enabled = False
from scapy.all import IP, UDP, IPOption, sr1

FLAG_PORT = 17777
FW_PORT = 17778
SOCKET_TIMEOUT = 3
RETRY_DELAY = 0.3
RETRY_COUNT = 4
ENCODING = "utf-8"

ID_LEN = 14  # cf5j-dxa9-6gpx
PASSWORD_LEN = 4

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

    def talk_scapy(self, port: int, passw: bytes, data: str):
        if len(passw) != 4:
            raise Exception("Wrong password length: {}".format(len(passw)))

        # For testing purposes.
        kwargs = dict()
        if os.environ.get("DEBUG_NO_OPTION") == "1":
            logging.info("DEBUG: don't send password in IP options")
            options = None
        elif os.environ.get("DEBUG_WRONG_PASS") == "1":
            logging.info("DEBUG: send wrong password in IP options")
            options = IPOption(b"\x30\x06\x00\x00\x00\x00")
        else:
            options = IPOption(b"\x30\x06" + passw)
        if options is not None:
            kwargs["options"] = options
        ans = sr1(IP(dst=self.host, **kwargs) /
                  UDP(sport=random.randrange(1024, 65535), dport=port) /
                  data, timeout=SOCKET_TIMEOUT, retry=RETRY_COUNT)
        if not ans:
            return None
        try:
            return bytes(ans[0][0][0][UDP].payload).decode()
        except IndexError as e:
            logging.error(str(e))
            return None

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
    truncated_pass_bytes = pass_bytes[0:4]
    return truncated_pass_bytes, "{:02x}{:02x}{:02x}{:02x}".format(*truncated_pass_bytes)


def create_signature(flag_id):
    time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_sign = (flag_id + ":" + time_str).encode()
    return "{}:{:x}".format(time_str, privkey.sign(data_to_sign, "")[0])


@fail_on_timeout
def check(ip):
    client = Client(ip)

    response = client.talk(FLAG_PORT, "PIN")
    if response == "PON":
        return ExitCode.OK

    print("PIN has failed.")  # Visible to team
    return ExitCode.MUMBLE


@fail_on_timeout
def put(ip, id, flag, *args):
    if len(id) != ID_LEN:
        raise Exception("Bad flag ID length: {}, should be {}.".format(len(id), ID_LEN))

    password, password_str = create_password(id)
    logging.debug("Calculated password (hex): %r", password_str)
    if len(password) != PASSWORD_LEN:
        raise Exception("Password error.")

    client = Client(ip)
    signature = create_signature(id)

    i = 1
    max_tries = 4
    while True:
        response = client.talk(FW_PORT, "LCK {} {} {}".format(id, password_str, signature))
        if response == "OK":
            break
        elif i >= max_tries:
            print("LCK has failed.")  # Visible to team
            return ExitCode.MUMBLE
        time.sleep(5)
        i += 1

    response = client.talk(FLAG_PORT, "PUT {} {} {}".format(id, flag, signature))
    if response != "OK":
        print("PUT has failed.")  # Visible to team
        return ExitCode.MUMBLE

    return ExitCode.OK


@fail_on_timeout
def get(ip, id, flag, *args):
    client = Client(ip)

    response = client.talk(FLAG_PORT, "DIR")
    if id not in response:
        print("Flag ID not found in DIR response.")  # Visible to team
        logging.error("Flag ID (%r) wasn't found in DIR response.", id)
        return ExitCode.CORRUPT

    password, password_str = create_password(id)
    logging.debug("Calculated password (hex): %r", password_str)
    if len(password) != PASSWORD_LEN:
        raise Exception("Password error.")

    response = client.talk_scapy(FLAG_PORT, password, "GET {}".format(id))
    if response != flag:
        print("Wrong flag data received.")  # Visible to team
        logging.error("Wrong flag data received [%r != %r].", response, flag)
        return ExitCode.CORRUPT

    logging.info("The flag was found.")
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
