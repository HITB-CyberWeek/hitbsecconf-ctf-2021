#!/bin/sh

set -e

TMPDIR=/work gcc -o /work/program /work/program.c
rm -r /usr/bin/gcc /bin/busybox

/work/program < /work/input > /work/output
