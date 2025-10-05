FROM ad8857/ros-llm:llama3.1-8b

# Source ROS and workspace automatically
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
    
ENV DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES=0 \
    OLLAMA_USE_GPU=1 \ 
    ROS_DISTRO=humble \
    ROS_DOMAIN_ID=0

# Install Langchain, Langgraph and other libraries
RUN pip install --no-cache-dir --pre -U \
    langchain \
    langchain-core \
    langchain-anthropic \
    langchain-aws \
    langchain-openai \
    langchain \
    langchain_ollama \
    langgraph \
    langgraph-sdk \
    langgraph-supervisor \
    langgraph-swarm \
    langchain-mcp-adapters \
    langmem \
    agentevals \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY /colcon_ws/ /colcon_ws/
COPY /entrypoint_scripts/ /entrypoint_scripts/

RUN chmod +x entrypoint_scripts/*

WORKDIR /colcon_ws/

RUN colcon build --symlink-install