#!/usr/bin/env bash
set -eu -o pipefail

pushd ./crds
trap popd EXIT

# install all crds defined locally
for FILE in *.yaml ; do
    echo "● installing CRD $(basename $FILE)"
    kubectl apply -f ${FILE}
done