#!/usr/bin/env python3
# Legacy storage service.
# Feel free to optimize :)

import logging
import os
import socket

from common import DB, check_signature

DATA_DIR = "/data/storage/"
PORT = 17777
MAX_SIZE = 64


def main():
    logging.basicConfig(level=logging.INFO, format="[storage] %(asctime)s %(message)s")

    flags = DB(DATA_DIR)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port {} ...".format(PORT))
    while True:
        message, address = sock.recvfrom(1024)
        message = message.decode("utf-8")
        logging.info("Received: {!r} from {!r}".format(message, address))

        response = "???"
        try:
            a = message.split(" ")
            if a[0] == "PIN":
                response = "PON"
            elif a[0] == "PUT":
                if check_signature(a[1], a[3]):
                    flags.put(key=a[1], value=a[2])
                    response = "OK"
                else:
                    response = "ERR_SIG"
            elif a[0] == "GET":
                response = flags.get(key=a[1], default="NO")
            elif a[0] == "DIR":
                if flags:
                    response = ",".join(sorted(flags.keys()))
                else:
                    response = "EMPTY"
            else:
                response = "ERR_CMD"
        except Exception:
            logging.exception("Exception")
            response = "ERR"

        logging.info("Sending response: %r", response)
        sock.sendto(bytes(response, "utf-8"), address)


if __name__ == "__main__":
    main()
