import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
from api.core.config_llm import llm
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

chat_engine = None

system_prompt = (
    "Você é um assistente jurídico especializado no Código de Defesa do Consumidor brasileiro.\n"
    "Responda APENAS com base nos documentos fornecidos.\n"
    "Sempre cite o artigo específico quando possível.\n"
    "Se não encontrar a resposta, diga claramente: 'Não encontrei essa informação no CDC'.\n"
    "Nunca invente leis ou artigos.\n"
    "Responda sempre em português."
)

def get_chat_engine():
    global chat_engine

    if chat_engine is None:
        
        Settings.embed_model = HuggingFaceEmbedding( # É necessário definir aqui, pois a transformação de texto em embedding tbm é usada na produção 
            model_name='intfloat/multilingual-e5-small'
        )
        db = chromadb.PersistentClient('chroma')
        collection = db.get_or_create_collection("documentos_llm")
        

        vector_store = ChromaVectorStore(collection)
        index = VectorStoreIndex.from_vector_store(vector_store)

        chat_engine = index.as_chat_engine(
            llm=llm,
            mode='simple',
            similarity_top_k=5,
            system_prompt=system_prompt
        )

    return chat_engine