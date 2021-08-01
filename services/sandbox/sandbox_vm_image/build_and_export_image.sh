#!/bin/bash

set -ex

wget -N https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-10.10.0-amd64-netinst.iso

packer build --force build.pkr.hcl
