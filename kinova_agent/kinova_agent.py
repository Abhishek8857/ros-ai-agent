import os

from rosa import ROSA
from .llm import get_llm
from .help import get_help
from .prompts import get_prompts
from langchain.agents import tool, Tool
from . import agent_tools

class KinovaAgent(ROSA):
    def __init__(self, streaming: bool = False, verbose: bool = True, ros_version: int = 2,accumulate_chat_history: bool = True):
        super().__init__(
            ros_version=ros_version,
            llm=get_llm(),
            tools=None,  
            tool_packages=[agent_tools],  
            prompts=get_prompts(), 
            verbose=verbose,
            accumulate_chat_history=accumulate_chat_history,
            streaming=streaming,
        )
        
    
    
        
        