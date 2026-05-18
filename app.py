# %% [markdown]
# ### Carregando documentos

# %%
from llama_index.core import SimpleDirectoryReader

# %% [markdown]
# Coloca os arquivos da pasta no objeto documents

# %%
documents = SimpleDirectoryReader(input_dir='files')
documents.input_files

# %%
docs = documents.load_data() # separa as páginas do arquivo

# %%a

# %% [markdown]
# ### Dividindo em partes menores

# %%
from llama_index.core.node_parser import SentenceSplitter

# %%
node_parser = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

# %%
nodes = node_parser.get_nodes_from_documents(docs, show_progress=True)



# %%


# %% [markdown]
# #### Gerando embeddings

# %%
import chromadb

# %% [markdown]
# Cria cliente e coleção


db = chromadb.PersistentClient('./chroma_db')
chroma_collection = db.get_or_create_collection("documentos_llm")

# %% [markdown]
# Define o modelo de embedding no llama-index

# %%
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# %%
Settings.embed_model = HuggingFaceEmbedding(model_name='intfloat/multilingual-e5-small')

# %% [markdown]
# Salvando Embedding no BD Chroma

# %%
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

# %%
vector_store = ChromaVectorStore(chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# %%
if chroma_collection.count() == 0:
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )
else:
    index = VectorStoreIndex.from_vector_store(vector_store)

# %% [markdown]
# Recuperação de informações

# %%
from dotenv import load_dotenv


# %%
import os

OPENAI_API = os.getenv('OPENAI_API_KEY')

# %%
from llama_index.llms.openai import OpenAI

llm = OpenAI(model='gpt-4o-mini', api_key=OPENAI_API)

# %%
Settings.llm = llm

# %%

# %%
system_prompt = (
    "Você é um advogado especialista no Código de Defesa do Consumidor brasileiro. "
    "Responda com base nos documentos fornecidos. "
    "Se encontrar um artigo relacionado, cite-o e explique de forma clara. "
    "Se não encontrar exatamente, use o artigo mais relevante disponível para responder."
)

# %% [markdown]
# Conversa interativa

# %%
chat_engine = index.as_chat_engine(llm=llm, mode='simple', similarity_top_k = 3, system_prompt = system_prompt )


# %%
import gradio as gr

# %%
def chat_bot(message, chat_history):
    MAX_INTERACTIONS = 5 

    
    if chat_history is None:
        chat_history = []

   
    interactions = len(chat_history) // 2

    
    if interactions >= MAX_INTERACTIONS:
        return "", chat_history + [
            {"role": "assistant", "content": "Limite de demonstração atingido."}
        ]

    try:
        response = chat_engine.chat(message)

        chat_history.append({'role': 'user', 'content': message})
        chat_history.append({'role': 'assistant', 'content': response.response})

        return "", chat_history

    except Exception as e:
        print("ERRO:", str(e))

        chat_history.append({
            "role": "assistant",
            "content": "Erro ao processar a resposta. Tente novamente mais tarde."
        })

        return "", chat_history



def reset_chat():
    chat_engine.reset()
    
    return [] 

# %%
with gr.Blocks() as demo:
    gr.Markdown("# Assistente Jurídico - Código de Defesa do consumidor")
    
    chatbot = gr.Chatbot(label='conversa', height=500)
    msg = gr.Textbox(label='Digite a sua mensagem')
    resetar = gr.Button('Limpar')
    
    msg.submit(chat_bot, [msg, chatbot], [msg, chatbot])
    resetar.click(reset_chat, None, chatbot, queue=False)
    
    demo.launch(server_name="0.0.0.0", server_port=7860)
