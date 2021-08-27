#!/usr/bin/env python3
import logging
import socket
import subprocess
import time

from common import DB, check_signature

DATA_DIR = "/data/protector/"
PORT = 17778
XDP_TEMPLATE_FILE = "xdp_filter.template.c"
XDP_RESULT_FILE = "xdp_filter.c"
XDP_REPLACEMENT = "$RULES$"
RULES_MAX_COUNT = 25


def generate_xdp_program(rules: DB):
    with open(XDP_TEMPLATE_FILE) as f:
        template = f.read()

    rules_program = ""
    for flag_id in sorted(rules.keys()):
        passw = rules.get(flag_id)
        flag_id_condition = " && ".join("udp_data[{}] == '{}'".format(i, c) for i, c in enumerate(flag_id, 4))

        rules_program += """
        if (%s) {
            if (ip_hdr->ihl > 5 && ip_options + 4 <= data_end && *(unsigned int *)ip_options == bpf_htonl(0x%s)) {
                return XDP_PASS; // Password check OK.
            }
            return XDP_DROP; // No password or wrong password - access denied.
        }
""" % (flag_id_condition, passw)
    xdp_program = template.replace(XDP_REPLACEMENT, rules_program)
    with open(XDP_RESULT_FILE, "w") as f:
        f.write(xdp_program)
    logging.info("XDP program was generated. %d rules.", len(rules.keys()))
    return True


def build_xdp_program():
    logging.info("Building XDP program...")
    try:
        subprocess.check_call("./xdp_filter_build.sh", shell=True, timeout=10)
    except subprocess.SubprocessError:
        logging.exception("Error building XDP program.")
        return False
    logging.info("XDP program was built.")
    return True


def retry_decorator(count: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            i = 1
            sleep_time = 0.5
            while True:
                logging.debug("Try %d of %d", i, count)
                if func(*args, **kwargs):
                    return True
                i += 1
                if i > count:
                    logging.warning("Call has failed. No more retries left.")
                    return False
                logging.warning("Call has failed. Retrying in %.1f sec..", sleep_time)
                time.sleep(sleep_time)
                sleep_time *= 2
        return wrapper
    return decorator


@retry_decorator(count=5)
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


def unload_xdp_program():
    logging.warning("Unloading XDP program")
    try:
        subprocess.check_call("./xdp_loader -d eth0 --filename xdp_filter.o --progsec xdp_main --unload",
                              shell=True, timeout=10)
    except subprocess.SubprocessError:
        logging.exception("Error unloading XDP program.")
        return False
    logging.info("XDP program was unloaded.")
    return True


def respond(sock, address, message):
    logging.info("Sending response: %r to %s", message, address)
    sock.sendto(bytes(message, "utf-8"), address)


def main():
    logging.basicConfig(level=logging.DEBUG, format="[protector] %(asctime)s %(message)s")

    rules = DB(DATA_DIR, limit=RULES_MAX_COUNT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    logging.info("Listening UDP port %d", PORT)

    if not generate_xdp_program(rules) or not build_xdp_program() or not load_xdp_program():
        logging.fatal("Cannot initialize XDP program, terminating.")
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

            rules.put(flag_id, passw)

            if not generate_xdp_program(rules):
                respond(sock, address, "ERR_GEN")
                continue

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
