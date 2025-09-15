#!/bin/bash

SCRIPT_DIR="$(dirname $(readlink -f $0))"
REPO_DIR="$(realpath "${SCRIPT_DIR}/..")"	
PARENT_DIR="$(realpath "${REPO_DIR}/..")"
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp


xhost +
docker run \
		-it \
		--net=host \
		--pid=host \
		--ipc=host \
		--privileged \
        --gpus all \
        --runtime=nvidia \
		-v /dev:/dev \
		-v $HOME/.ros/log:/.ros/log \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		--env RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION} \
		--env DISPLAY=$DISPLAY \
        --name agent \
        -v "$REPO_DIR:/agent_ws/src/ros-ai-agent:rw" \
        -w /workspace/ \
        ai-agent:latest \