import os
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

load_dotenv()

#API_OPENAI = os.getenv('OPENAI_API_KEY')
GROQ_API = os.getenv('GROQ_API')

llm = Groq(model="llama-3.3-70b-versatile", api_key=GROQ_API)

Settings.llm = llm



