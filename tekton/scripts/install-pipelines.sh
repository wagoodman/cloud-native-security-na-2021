#!/usr/bin/env bash
set -eu -o pipefail

pushd ./pipelines
trap popd EXIT

# install all pipelines defined locally
for DIR in */ ; do
    if [ -d "$DIR" ]; then
        echo "● installing pipeline $(basename $DIR)"
        kubectl apply -f ${DIR}/*.yaml
    fi
done