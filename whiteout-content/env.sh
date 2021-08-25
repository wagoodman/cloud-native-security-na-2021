# relative to the host filesystem
export ORIGINAL_IMAGE_TAR=./image-original.tar
export IMAGE_DIR=./image
export PAYLOAD_FILE=./payload.txt
export FINAL_IMAGE_TAR=./image-modified.tar
export FINAL_IMAGE_TAG=localhost/whiteout-content:modified

# relative to the container filesystem
export WHITEOUT_PATH=/somewhere/.wh.nothing.txt
export WHITEOUT_LAYER=3