#!/bin/bash
docker run -it --rm \
    -u root \
    --gpus all \
    --net=host \
    --ipc=host \
    -e QT_X11_NO_MITSHM=1 \
    -e DISPLAY=$DISPLAY \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display \
    -e LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib/i386-linux-gnu:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    carlatest:latest
