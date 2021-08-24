#!/bin/bash
set -ex
docker run --rm --cap-add=NET_ADMIN --cap-add=CAP_SYS_ADMIN -it flags.stub 
