#!/usr/bin/env python3
import logging
import socket
import subprocess

from common import DB, check_signature

DATA_DIR = "/data/protector/"
PORT = 17778


def build_xdp_program():
    logging.info("Building XDP program...")
    try:
        subprocess.check_call("./xdp_filter_build.sh", shell=True, timeout=10)
    except subprocess.SubprocessError:
        logging.exception("Error building XDP program.")
        return False
    logging.info("XDP program was built.")
    return True


def load_xdp_program():
    logging.info("Loading XDP program...")
    try:
        subprocess.check_call("./xdp_loader -d eth0 --filename xdp_filter.o --progsec xdp_main --force",
                              shell=True, timeout=10)
    except subprocess.SubprocessError:
        logging.exception("Error loading XDP program.")
        return False
    logging.info("XDP program was loaded.")
    return True


def respond(sock, address, message):
    logging.info("Sending response: %r to %s", message, address)
    sock.sendto(bytes(message, "utf-8"), address)


def main():
    logging.basicConfig(level=logging.DEBUG, format="[protector] %(asctime)s %(message)s")

    rules = DB(DATA_DIR)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port %d", PORT)

    if not build_xdp_program() or not load_xdp_program():
        return

    while True:
        try:
            message, address = sock.recvfrom(1024)
            message = message.decode("utf-8")
            logging.info("Received: %r from %s", message, address)

            tokens = message.split(" ")
            if len(tokens) != 4:
                respond(sock, address, "ERR_PROTO")
                continue

            cmd, flag_id, passw, signature = tokens
            if cmd != "LCK":
                respond(sock, address, "ERR_CMD")
                continue

            if not check_signature(flag_id, signature):
                respond(sock, address, "ERR_SIG")
                continue




            # generate_xdp_program()
            if not build_xdp_program():
                respond(sock, address, "ERR_BUILD")
                continue
            if not load_xdp_program():
                respond(sock, address, "ERR_LOAD")
                continue
            respond(sock, address, "OK")
        except Exception:
            logging.exception("Error")


if __name__ == "__main__":
    main()
