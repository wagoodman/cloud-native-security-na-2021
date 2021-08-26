# relative to the host filesystem
export ORIGINAL_IMAGE_TAR=./image-original.tar
export ORIGINAL_IMAGE_TAG=localhost/whiteout-content:original-by-addition
export IMAGE_DIR=./image
export PAYLOAD_FILE=./payload.txt
export FINAL_IMAGE_TAR=./image-modified.tar
export FINAL_IMAGE_TAG=localhost/whiteout-content:modified-by-addition

# relative to the container filesystem
export WHITEOUT_PATH=/somewhere/.wh.nothing.txt
export WHITEOUT_LAYER=3

function dkr {
    # vol 1: for the build context and dockerfile
    # vol 2: for credentials to push to docker hub or a registry
    docker run --rm -it \
        --name img \
        --volume $(pwd):/home/user/src \
        --workdir /home/user/src \
        --volume "${HOME}/.docker:/root/.docker:ro" \
        --security-opt seccomp=unconfined --security-opt apparmor=unconfined \
        r.j3ss.co/img \
            "$@"
}
