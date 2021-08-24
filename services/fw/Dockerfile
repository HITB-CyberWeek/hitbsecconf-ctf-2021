FROM python:3.6-slim

RUN mkdir -p /ctf

WORKDIR /ctf

RUN apt-get update && apt-get install -y procps iproute2 clang libc6-dev-i386 llvm

COPY . .

ENTRYPOINT ./entrypoint.sh
