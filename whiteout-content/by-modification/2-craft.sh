#!/usr/bin/env bash
set -eux

source env.sh

# attach a payload by inserting bytes into a specific whiteout file
poetry run python ./image-manipulator.py \
                    attach-payload \
                        --dir ${IMAGE_DIR} \
                        --payload ${PAYLOAD_FILE} \
                        --layer ${WHITEOUT_LAYER} \
                        --path ${WHITEOUT_PATH}
