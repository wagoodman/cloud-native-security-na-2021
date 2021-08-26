#!/usr/bin/env bash
set -eux

source env.sh

chmod 600 payload.txt

# build and save the image into a tar + extract it for use
dkr build --no-cache -t ${ORIGINAL_IMAGE_TAG} -o type=oci,dest=${ORIGINAL_IMAGE_TAR} .

rm -rf ${IMAGE_DIR} || true
mkdir ${IMAGE_DIR}
tar -xvf ${ORIGINAL_IMAGE_TAR} -C ${IMAGE_DIR}
