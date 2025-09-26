FROM  ad8857/ros-llm-gpt:v1.0

# Install Langchain, Langgraph and other libraries
RUN pip install --no-cache-dir -U \
    langchain \
    langchain_ollama \
    langgraph \
    langgraph-sdk \
    langgraph-supervisor \
    langgraph-swarm \
    langchain-mcp-adapters \
    langmem \
    agentevals \
    langgraph-cli[inmem] \
    langsmith

COPY /colcon_ws/ /colcon_ws/
COPY /entrypoint_scripts/ /entrypoint_scripts/

RUN chmod +x entrypoint_scripts/*

WORKDIR /colcon_ws/

RUN colcon build --symlink-install

# ARG ROS_DISTRO=humble
# FROM osrf/ros:${ROS_DISTRO}-desktop

# # Use bash for all RUN commands after this line
# SHELL ["/bin/bash", "-c"]

# # Set the ROS Domain ID and Middleware
# ENV ROS_DOMAIN_ID=0 \
#     RMW_IMPLEMENTATION=rmw_cyclonedds_cpp 

# # Install required dependencies
# RUN apt-get update && apt-get install --no-install-recommends -y \
#     wget \
#     lsb-release \
#     gnupg \
#     build-essential \
#     cmake \
#     git \
#     pciutils \
#     iputils-ping \
#     ament-cmake \
#     python3-pip \
#     python3-colcon-common-extensions \
#     python3-vcstool \
#     ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# # Source ROS and workspace automatically
# RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc



