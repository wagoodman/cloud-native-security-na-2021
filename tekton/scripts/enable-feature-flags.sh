#!/usr/bin/env bash
set -u

# in order to use Task.step onError feature, we must use "enable-api-fields"="alpha" to allow alpha fields to be used in Tasks and Pipelines.

kubectl patch configmap feature-flags -n tekton-pipelines -p '{"data": {"enable-api-fields": "alpha"}}'
