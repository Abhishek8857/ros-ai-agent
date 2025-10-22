FROM ad8857/ros-llm:llama3.1-8b

# Source ROS and workspace automatically
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
    
ENV DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES=0 \
    OLLAMA_USE_GPU=1 \ 
    ROS_DISTRO=humble \
    ROS_DOMAIN_ID=0

# Install Langchain, Langgraph and other libraries
RUN pip install --no-cache-dir -U \
    langchain==1.0.2 \
    langchain-core==1.0.0 \
    langchain-anthropic==1.0.0 \
    langchain-aws==1.0.0 \
    langchain-openai==1.0.1 \
    langchain_ollama==1.0.0 \
    langgraph==1.0.1 \
    langgraph-sdk==0.2.9 \
    langmem==0.0.28 \
    agentevals==0.0.9 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY /colcon_ws/ /colcon_ws/
COPY /entrypoint_scripts/ /entrypoint_scripts/

RUN chmod +x entrypoint_scripts/*

WORKDIR /colcon_ws/

RUN colcon build --symlink-install