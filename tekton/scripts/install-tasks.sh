#!/usr/bin/env bash
set -eu -o pipefail

pushd ./tasks
trap popd EXIT

install_refs() {
    echo "● installing task references from $1"
    while IFS= read -r LINE; do
        IFS=":" read NAME URL <<< "$LINE"
        kubectl apply -f $URL
    done < $1
}

export -f install_refs

# install any tasks from references
find . -name '*-refs.yaml' | xargs -I {} bash -c 'install_refs "{}"'

# install all tasks defined locally
for DIR in */ ; do
    if [ -d "$DIR" ]; then
        echo "● installing custom task $(basename $DIR)"
        kubectl apply -f ${DIR}/*.yaml
    fi
done