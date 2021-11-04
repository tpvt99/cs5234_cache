#!/bin/bash

# to build:
# docker build -t simple_linux .

docker run -it --security-opt seccomp=default.json \
    -v $PWD:/proj -m 8m --memory-swap -1 simple_linux;