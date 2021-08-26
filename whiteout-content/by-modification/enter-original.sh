#!/usr/bin/env bash
set -eux

source env.sh

LOAD_ID=$(docker load -i ${ORIGINAL_IMAGE_TAR} | sed -n 's/^Loaded image ID: sha256:\([0-9a-f]*\).*/\1/p')

docker run --rm -it ${LOAD_ID} sh