import os
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent / ".env" # Configurando a localização do .env
load_dotenv(dotenv_path=env_path)

#API_OPENAI = os.getenv('OPENAI_API_KEY')
GROQ_API = os.getenv('GROQ_API')

llm = Groq(model="openai/gpt-oss-120b", api_key=GROQ_API, temperature=0.3, context_window=131072, max_tokens=1024)

Settings.llm = llm



