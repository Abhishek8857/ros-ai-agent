FROM ad8857/ros-llm:llama3.1-8b

# Source ROS and workspace automatically
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
    
ENV DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES=0 \
    OLLAMA_USE_GPU=1 \ 
    ROS_DISTRO=humble \
    ROS_DOMAIN_ID=0

# Install Langchain, Langgraph and other libraries

# RUN pip install --no-cache-dir -U \
#     langchain \
#     langchain-core \
#     langchain-anthropic \
#     langchain-aws \
#     langchain-openai \
#     langchain_ollama \
#     langgraph \
#     langgraph-sdk \
#     langmem \
#     agentevals \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

    
RUN pip install --no-cache-dir -U \
    langchain==1.0.5     \
    langchain-core==1.0.4 \
    langchain-anthropic==1.0.3 \
    langchain-aws==1.0.0 \
    langchain-openai==1.0.2 \
    langchain_ollama==1.0.0 \
    langgraph==1.0.3 \
    langgraph-sdk==0.2.9 \
    langmem==0.0.30 \
    agentevals==0.0.9 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY /colcon_ws/ /colcon_ws/
COPY /entrypoint_scripts/ /entrypoint_scripts/

RUN chmod +x entrypoint_scripts/*

WORKDIR /colcon_ws/

RUN colcon build --symlink-install


# FOR GPG KEY Error

##########################
# 1️⃣ Clean old ROS2 repos and keys
##########################
# RUN rm -f /etc/apt/sources.list.d/ros2.list \
#     /etc/apt/sources.list.d/ros-latest.list \
#     /usr/share/keyrings/ros-archive-keyring.gpg \
#     /usr/share/keyrings/ros2-latest-archive-keyring.gpg || true

##########################
# 2️⃣ Update APT and install essentials
##########################
# RUN apt-get update --allow-releaseinfo-change || true
# RUN apt-get install -y --no-install-recommends \
#     curl gnupg2 lsb-release ca-certificates wget python3-pip

##########################
# 3️⃣ Add new ROS2 GPG key
##########################
# RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
#     -o /usr/share/keyrings/ros2-latest-archive-keyring.gpg

##########################
# 4️⃣ Add ROS2 repo using the new key
##########################
# RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-latest-archive-keyring.gpg] \
#     http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
#     > /etc/apt/sources.list.d/ros2.list