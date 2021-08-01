#!/bin/sh

set -e

cd /work

gcc -o program program.c
./program < input > output
