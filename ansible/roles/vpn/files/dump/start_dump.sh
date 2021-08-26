#!/bin/bash

mkdir -p /mnt/traffic/big
chown -R dump:dump /home/dump /mnt/traffic
cd /mnt/traffic/big
exec tcpdump -B 1000000 -s 0 -w dump -n -i nflog:1 -C 100 -z '/home/dump/rotate_dump.sh' -Z dump
