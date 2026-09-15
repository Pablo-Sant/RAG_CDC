from llama_index.core import VectorStoreIndex
from api.core.config_llm import llm
from llama_index.core import Settings
from api.core.database import get_index
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

chat_engine = None

system_prompt = (
    "Você é um assistente jurídico especializado no Código de Defesa do Consumidor brasileiro.\n"
    "Responda APENAS com base nos documentos fornecidos.\n"
    "Sempre cite o artigo específico quando possível.\n"
    "Se não encontrar a resposta, diga claramente: 'Não encontrei essa informação no CDC'.\n"
    "Nunca invente leis ou artigos.\n"
)

def get_chat_engine():
    global chat_engine

    if chat_engine is None:
        
        Settings.embed_model = HuggingFaceEmbedding( # É necessário definir aqui, pois a transformação de texto em embedding tbm é usada na produção 
            model_name='intfloat/multilingual-e5-small'
        )
        
        pinecone_index = get_index()
         

        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        index = VectorStoreIndex.from_vector_store(vector_store)

        chat_engine = index.as_chat_engine(
            llm=llm,
            mode='context',
            similarity_top_k=5,
            system_prompt=system_prompt
        )

    return chat_engine