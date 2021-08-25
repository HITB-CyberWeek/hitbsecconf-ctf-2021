#!/usr/bin/env python3
# Legacy storage service.
# Feel free to optimize :)

import logging
import os
import socket

DATA_DIR = "/data/"
PORT = 17777
MAX_SIZE = 64


def check_signature(a):
    return True  # FIXME


def load_flags():
    flags = dict()
    try:
        for fname in os.listdir(DATA_DIR):
            full_name = os.path.join(DATA_DIR, fname)
            if os.path.isfile(full_name) and os.path.getsize(full_name) <= MAX_SIZE:
                with open(full_name) as f:
                    data = f.read()
                flags[fname] = data
        logging.info("Loaded %d flags from disk", len(flags))
    except Exception:
        logging.exception("Loading flags from disk has failed")
    return flags


def main():
    logging.basicConfig(level=logging.INFO, format="[storage] %(asctime)s %(message)s")

    flags = load_flags()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port {} ...".format(PORT))
    while True:
        message, address = sock.recvfrom(1024)
        message = message.decode("utf-8")
        logging.info("Received: {!r} from {!r}".format(message, address))
        try:
            a = message.split(" ")
            if a[0] == "PIN":
                response = "PON"
            elif a[0] == "PUT":
                if check_signature(a):
                    flags[a[1]] = a[2]
                    with open(os.path.join(DATA_DIR, a[1]), "w") as f:
                        f.write(a[2])
                    response = "OK"
                else:
                    response = "ERRSIG"
            elif a[0] == "GET":
                response = flags.get(a[1], "NO")
            elif a[0] == "DIR":
                if flags:
                    response = ",".join(sorted(flags.keys()))
                else:
                    response = "EMPTY"
            else:
                response = "ERRCMD"
        except Exception:
            logging.exception("Exception")
            response = "ERR"

        logging.info("Sending response: %r", response)
        sock.sendto(bytes(response, "utf-8"), address)


if __name__ == "__main__":
    main()
