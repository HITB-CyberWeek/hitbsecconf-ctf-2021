#!/bin/bash
set -ex
cd "$(dirname $0)"
NAME=xdp_filter
clang -S \
    -target bpf \
    -D __BPF_TRACING__ \
    -Wall \
    -Wno-unused-value \
    -Wno-pointer-sign \
    -Wno-compare-distinct-pointer-types \
    -Werror \
    -O2 -emit-llvm -c -g -o $NAME.ll $NAME.c
llc -march=bpf -filetype=obj -o $NAME.o $NAME.ll
