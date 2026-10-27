from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from pathlib import Path
import traceback
import os

env_path = Path(__file__).resolve().parent.parent / ".env" # Configurando a localização do .env
load_dotenv(dotenv_path=env_path) 

pinecone_api = os.getenv('PINECONE_API_KEY')


def create_index():
    try:
        pc = Pinecone(api_key=pinecone_api)

        if "rag-cdc" not in pc.list_indexes().names():    
            pc.create_index(
                name="rag-cdc",
                dimension=384,  
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1") 
            )
            
        else:
            print("índice 'rag-cdc' já existe")
            
        return pc
    
    except Exception as e:
        traceback.print_exc()
        print(f"Erro na criação do banco: {e}")
        raise


def get_index():
    try:
        pc = Pinecone(api_key=pinecone_api)
        index = pc.Index("rag-cdc")
        
        return index
    
    except Exception as e:
        print("Erro na conexão com o banco", e)
        raise
    
