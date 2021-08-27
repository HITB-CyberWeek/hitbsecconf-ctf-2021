#!/usr/bin/env python3
# Legacy storage service.
# Feel free to optimize :)

import logging
import socket

from common import DB, check_signature

DATA_DIR = "/data/storage/"
PORT = 17777
MAX_SIZE = 64
ITEMS_MAX_COUNT = 25


def main():
    logging.basicConfig(level=logging.DEBUG, format="[ storage ] %(asctime)s %(message)s")

    flags = DB(DATA_DIR, limit=ITEMS_MAX_COUNT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port {} ...".format(PORT))
    while True:
        message, address = sock.recvfrom(1024)
        message = message.decode("utf-8")
        logging.info("Received: {!r} from {!r}".format(message, address))

        response = "???"
        try:
            cmd = message[:3]
            if cmd == "PIN":
                response = "PON"
            elif cmd == "PUT":
                flag_id = message[4:18]
                flag_data, signature = message[19:].split(" ")
                if check_signature(flag_id, signature):
                    flags.put(key=flag_id, value=flag_data)
                    response = "OK"
                else:
                    response = "ERR_SIG"
            elif cmd == "GET":
                flag_id = message[4:18]
                response = flags.get(key=flag_id, default="NO")
            elif cmd == "DIR":
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
