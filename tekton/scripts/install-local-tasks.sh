#!/usr/bin/env bash
set -eu -o pipefail

pushd ./tasks
trap popd EXIT

# install all tasks defined locally
for DIR in */ ; do
    if [ -d "$DIR" ]; then
        echo "● installing custom task $(basename $DIR)"
        kubectl apply -f ${DIR}/*.yaml
    fi
done