#!/usr/bin/env bash
set -eux -o pipefail

source env.sh

# does the file exist in the squash representation?
TARGET_DIR_LISTING=$(docker run --rm -it ${FINAL_IMAGE_TAG} ls -1 $(dirname ${WHITEOUT_PATH}))

# does the image have the whiteout file contents?
VERIFY_IMAGE_TAR=${FINAL_IMAGE_TAR}+verify
VERIFY_IMAGE_DIR=${IMAGE_DIR}+verify

docker image save ${FINAL_IMAGE_TAG} -o ${VERIFY_IMAGE_TAR}
rm -rf ${VERIFY_IMAGE_DIR} || true
mkdir ${VERIFY_IMAGE_DIR}
tar -xvf ${VERIFY_IMAGE_TAR} -C ${VERIFY_IMAGE_DIR}


WHITEOUT_CONTENTS=$(poetry run python ./image-manipulator.py \
                        get-layer-path-contents \
                            --dir ${VERIFY_IMAGE_DIR} \
                            --layer ${WHITEOUT_LAYER} \
                            --path ${WHITEOUT_PATH})

EXPECTED_PAYLOAD=$(cat ${PAYLOAD_FILE})

set +x

echo
echo -n "Test if target file is removed:       "
if [ -z "${TARGET_DIR_LISTING}" ]
then
      echo "Pass!"
else
      echo "FAIL: found a directory listing: ${TARGET_DIR_LISTING}"
fi


echo -n "Test if container image has payload:  "
if [[ "${WHITEOUT_CONTENTS}" == "${EXPECTED_PAYLOAD}" ]]
then
      echo "Pass!"
else
      echo "FAIL: could not find payload"
      echo "   expected: ${EXPECTED_PAYLOAD}"
      echo "        got: ${WHITEOUT_CONTENTS}"
fi
