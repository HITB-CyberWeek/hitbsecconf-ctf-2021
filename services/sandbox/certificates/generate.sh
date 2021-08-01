#!/bin/bash

# Follow the instructions on https://docs.docker.com/engine/security/protect-access/#create-a-ca-server-and-client-keys-with-openssl

# CA key generating
openssl genrsa -aes256 -out ca.key.pem 4096
openssl req -subj "/CN=ca.sandbox.2021.ctf.hitb.org" -new -x509 -days 265 -key ca.key.pem -sha256 -out ca.pem

# Server key generating
openssl genrsa -out docker.key.pem 4096
openssl req -subj "/CN=docker.sandbox.2021.ctf.hitb.org" -sha256 -new -key docker.key.pem -out docker.csr

# Sign the request
openssl x509 -req -days 365 -sha256 -in docker.csr -CA ca.pem -CAkey ca.key.pem -CAcreateserial -out docker.pem
