import os
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from dotenv import load_dotenv

load_dotenv()

#API_OPENAI = os.getenv('OPENAI_API_KEY')
GROQ_API = os.getenv('GROQ_API')

llm = Groq(model="openai/gpt-oss-120b", api_key=GROQ_API, temperature=0.3, context_window=131072, max_tokens=1024)

Settings.llm = llm



