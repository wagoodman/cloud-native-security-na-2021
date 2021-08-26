#!/usr/bin/env bash
set -eux

./1-build.sh
./2-craft.sh
./3-import.sh
./4-verify-delivery.sh
