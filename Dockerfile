FROM ad8857/ros-llm:llama3.1-8b

# Source ROS and workspace automatically
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc

# Use bash for all RUN commands after this line
SHELL ["/bin/bash", "-c"]

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
#     google-genai \
#     Pillow \
#     numpy==1.24.0 \
#     dotenv \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

    
RUN pip install --no-cache-dir -U \
    python-dotenv \
    langchain==1.2.10 \
    langchain-core==1.2.16 \
    langchain-anthropic==1.3.4 \
    langchain-aws==1.3.0 \
    langchain-openai==1.1.10 \
    langchain_ollama==1.0.1 \
    langgraph==1.0.9 \
    langgraph-sdk==0.3.9 \
    langmem==0.0.30 \
    agentevals==0.0.9 \
    google-genai==1.65.0 \
    Pillow==12.1.1 \
    numpy==1.24.0 \
    dotenv==0.9.9 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY /colcon_ws/ /colcon_ws/
COPY /entrypoint_scripts/ /entrypoint_scripts/

RUN chmod +x entrypoint_scripts/*

WORKDIR /colcon_ws/

RUN source /opt/ros/${ROS_DISTRO}/setup.bash && colcon build --symlink-install



# FOR GPG KEY Error

##########################
# Clean old ROS2 repos and keys
##########################
# RUN rm -f /etc/apt/sources.list.d/ros2.list \
#     /etc/apt/sources.list.d/ros-latest.list \
#     /usr/share/keyrings/ros-archive-keyring.gpg \
#     /usr/share/keyrings/ros2-latest-archive-keyring.gpg || true

##########################
#  Update APT and install essentials
##########################
# RUN apt-get update --allow-releaseinfo-change || true
# RUN apt-get install -y --no-install-recommends \
#     curl gnupg2 lsb-release ca-certificates wget python3-pip

##########################
#  Add new ROS2 GPG key
##########################
# RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
#     -o /usr/share/keyrings/ros2-latest-archive-keyring.gpg

##########################
# Add ROS2 repo using the new key
##########################
# RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-latest-archive-keyring.gpg] \
#     http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
#     > /etc/apt/sources.list.d/ros2.list