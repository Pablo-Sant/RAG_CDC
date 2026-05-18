from llama_index.core import SimpleDirectoryReader 
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex


Settings.embed_model = HuggingFaceEmbedding(model_name='intfloat/multilingual-e5-small')


def build_index():
   # Carregar os documentos 
   documents = SimpleDirectoryReader(input_dir='../files')
   documents.input_files
   documents = documents.load_data() 
   print('Carregamento executado com sucesso')
   
   # Dividindo em chunks
   node_parser = SentenceSplitter(chunk_size=1000, chunk_overlap=200)
   nodes = node_parser.get_nodes_from_documents(documents)
   print('chunkzação executada com sucesso')
   
   # Criando o banco de dados
   db = chromadb.PersistentClient('../chroma')
   chroma_collection = db.get_or_create_collection('documentos_llm')
   print('banco criado com sucesso')
   
   # Criando Vector store
   vector_store = ChromaVectorStore(chroma_collection)
   storage_context = StorageContext.from_defaults(vector_store=vector_store)
   print('Vector Store criado com sucesso')
   
   # Criando os embeddings e colocando no banco
   VectorStoreIndex(nodes, storage_context=storage_context)
   print('Embeddings feitos com sucesso')
   
build_index()
   
   