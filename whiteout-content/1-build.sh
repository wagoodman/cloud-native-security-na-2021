#!/usr/bin/env bash
set -eux

source env.sh

IIDFILE=$(mktemp) || exit 1
trap 'rm -f "${IIDFILE} ${ORIGINAL_IMAGE_TAR} ${FINAL_IMAGE_TAR}"' EXIT

# build and save the image into a tar + extract it for use
docker build --iidfile ${IIDFILE} .

docker image save $(cat ${IIDFILE}) -o ${ORIGINAL_IMAGE_TAR}
rm -rf ${IMAGE_DIR} || true
mkdir ${IMAGE_DIR}
tar -xvf ${ORIGINAL_IMAGE_TAR} -C ${IMAGE_DIR}
