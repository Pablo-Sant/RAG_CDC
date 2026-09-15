from pinecone import Pinecone
import os
from dotenv import load_dotenv


load_dotenv()



try:  
    
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index("rag-cdc")

    index.delete(delete_all=True)
    
    print("Índice deletado com sucesso")

    
except Exception as e:
    print(f"Erro ao apagar vetores do índice rag-cdc {e}")
 