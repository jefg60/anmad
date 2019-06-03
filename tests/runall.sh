#!/usr/bin/env bash

python ./test_*.py || exit 1
bats tests/anmad.bats

