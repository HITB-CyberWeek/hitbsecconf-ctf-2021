#!/usr/bin/env python3
import logging
import socket
import subprocess

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


def main():
    logging.basicConfig(level=logging.INFO, format="[protector] %(asctime)s %(message)s")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port %d", PORT)

    # if not build_xdp_program() or not load_xdp_program():
    #     return

    while True:
        message, address = sock.recvfrom(1024)
        message = message.decode("utf-8")
        logging.info("Received: %r", message)

        # update_state()
        # generate_xdp_program()
        if not build_xdp_program():
            sock.sendto(bytes("ERR:B", "utf-8"), address)
            continue
        if not load_xdp_program():
            sock.sendto(bytes("ERR:L", "utf-8"), address)
            continue
        sock.sendto(bytes("OK", "utf-8"), address)


if __name__ == "__main__":
    main()
