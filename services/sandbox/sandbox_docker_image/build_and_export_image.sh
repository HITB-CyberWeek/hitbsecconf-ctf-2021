#!/bin/bash

set -ex

docker build -t sandbox .
docker save sandbox | gzip > sandbox.tar.gz
