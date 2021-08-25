#!/bin/bash

set -ex

wget -N https://cdimage.debian.org/cdimage/archive/10.10.0/amd64/iso-cd/debian-10.10.0-amd64-netinst.iso

packer build --force build.pkr.hcl

# Due to https://www.virtualbox.org/ticket/19440
rm output-sandbox/*.mf
