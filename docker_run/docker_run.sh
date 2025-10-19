#!/bin/bash

# Get directory paths
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_DIR="$(realpath "${SCRIPT_DIR}/..")"	
PARENT_DIR="$(realpath "${REPO_DIR}/..")"

# Set ROS middleware
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Allow GUI access
xhost +local:docker

# Run Docker
docker run \
    -it \
    --rm \
    --net=host \
    --pid=host \
    --ipc=host \
    --privileged \
    --gpus all \
    --runtime=nvidia \
    -v /dev:/dev \
    -v "$HOME/.ros/log:/root/.ros/log" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$REPO_DIR:/ros-ai-agent:rw" \
    -v "$PARENT_DIR:/root/workspaces/thesis_ws/src:rw" \
    -w /ros-ai-agent \
    -e RMW_IMPLEMENTATION \
    -e DISPLAY \
    --name ros_ai_agent \
    agent:latest \
    /entrypoint_scripts/entrypoint_docker_run.sh
