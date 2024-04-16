#!/bin/bash

# the args passed to the script
COMMANDS=(${@-west build -b native_sim_64})

docker run -it --rm \
       --platform=linux/arm64 \
       -v $(pwd)/../mytemp:/work \
       -v $(pwd):/work/myrotate \
       --workdir /work/myrotate \
       -e "ZEPHYR_TOOLCHAIN_VARIANT=host" \
       myrotate-builder:latest ${COMMANDS[@]}
