from langchain_ollama import ChatOllama
from .agent_tools import get_tools
from openai import OpenAI

language_model = "llama3.1"
mistral_cloud = "mistral-large-3:675b-cloud"
mistral_small = "mistral-small3.2"
mistral = 'mistral'
# pip install langchain==0.3.7
#mixtral8x7b = 'mixtral:8x7b'

language_model_temperature = 0.8

def get_llm():
    return ChatOllama(model=language_model, 
                      temperature=language_model_temperature
                      ).bind_tools(get_tools())

# api_key= ""
# base_url= "https://chat-ai.academiccloud.de/v1"
# model = "mistral-large-3-675b-instruct-2512"

# client = OpenAI(api_key=api_key,
#                 base_url=base_url)

# chat_completion = client.chat.completions.create(
#         messages=[{"role":"system","content":"You are a helpful assistant"},{"role":"user","content":"How tall is the Eiffel tower?"}],
#         model= model,
#     )

# print(chat_completion)