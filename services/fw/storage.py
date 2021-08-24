#!/usr/bin/env python3
# Simple service stub to test checker code.

import socket
port = 17777

flags = dict()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", port))
print("Listening port {} ...".format(port))
while True:
    message, address = sock.recvfrom(1024)
    message = message.decode("utf-8")
    print("Received: {!r} from {!r}".format(message, address))
    try:
        a = message.split(" ")
        if a[0] == "PIN":
            response = "PON"
        elif a[0] == "PUT":
            flags[a[1]] = a[2]
            response = "OK"
        elif a[0] == "GET":
            response = flags.get(a[1], "NO")
        elif a[0] == "DIR":
            response = ",".join(sorted(flags.keys()))
        else:
            response = "UNK"
    except Exception as e:
        response = "ERR"

    sock.sendto(bytes(response, "utf-8"), address)
