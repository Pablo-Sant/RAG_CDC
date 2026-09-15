from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()

pinecone_api = os.getenv('PINECONE_API_KEY')

def create_index():
    try:
        pc = Pinecone(api_key=pinecone_api)

        if "rag-cdc" not in pc.list_indexes().names():    
            pc.create_index(
                name="rag-cdc",
                dimension=384,  # bate com intfloat/multilingual-e5-small
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1") 
            )
            
        else:
            print("índice 'rag-cdc' já existe")
            
        return pc
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Erro na criação do banco: {e}")
        return None


def get_index():
    try:
        pc = Pinecone(api_key=pinecone_api)
        index = pc.Index("rag-cdc")
        
        return index
    
    except Exception:
        print("Erro na conexão com o banco")
    
