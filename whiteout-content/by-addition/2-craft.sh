#!/usr/bin/env bash
set -eux

source env.sh

# re-write the config history to show that the file was removed
poetry run python ./image-manipulator.py \
                    change-metadata \
                        --dir ${IMAGE_DIR} \
                        --layer ${WHITEOUT_LAYER}
