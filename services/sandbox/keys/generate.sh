#!/bin/bash

ssh-keygen -t rsa -b 4096 -C "sandbox@docker.sandbox.2021.ctf.hitb.org" -f ./id_rsa -q -N ""
