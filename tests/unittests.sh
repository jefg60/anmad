#!/usr/bin/env bash

for i in ./test_*.py
do
  echo unit testing $i
  python $i || exit 1
done
