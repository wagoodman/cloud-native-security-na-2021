#!/usr/bin/env bash
set -eux

source env.sh

docker run --rm -it ${FINAL_IMAGE_TAG} sh