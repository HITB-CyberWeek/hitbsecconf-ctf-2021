#!/bin/sh

set -e

gcc -o /work/program /work/program.c
rm -r /usr/bin/gcc /bin/busybox

/work/program < /work/input > /work/output
