#!/usr/bin/env bash
set -eux -o pipefail

source env.sh

# tar up the dir into a modified image tar
tar -C ${IMAGE_DIR} -cvf ${FINAL_IMAGE_TAR} .

# docker load the image
LOAD_ID=$(docker load -i ${FINAL_IMAGE_TAR} | sed -n 's/^Loaded image ID: sha256:\([0-9a-f]*\).*/\1/p')

# tag it to more easily find/use it
docker tag ${LOAD_ID} ${FINAL_IMAGE_TAG}
