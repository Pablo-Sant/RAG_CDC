from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from api.core.database import create_index
import pdfplumber
import re
import os



INSTRUMENTOS = [
    (12,  "Lei 8.078/1990",          "lei"),
    (95,  "Decreto 4.680/2003",      "decreto"),
    (99,  "Decreto 5.440/2005",      "decreto"),
    (125, "Decreto 7.962/2013",      "decreto"),
    (129, "Decreto 7.963/2013",      "decreto"),
    (140, "Portaria MJ 81/2002",     "portaria"),
    (143, "Portaria MJ 2.658/2003",  "portaria"),
    (146, "Portaria MJ 2.014/2008",  "portaria"),
    (149, "Portaria MJ 49/2009",     "portaria"),
    (152, "Portaria MJ 487/2012",    "portaria"),
]


def instrumento_da_pagina(num_pagina_zero_based: int) -> tuple[str, str]:
    
    nome, tipo = "Documento não identificado", "desconhecido"
    for pg_inicio, n, t in INSTRUMENTOS:
        if num_pagina_zero_based >= pg_inicio:
            nome, tipo = n, t
    return nome, tipo


def extrair_texto_por_pagina(pdf_path: str) -> list[dict]:

    paginas = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            texto = page.extract_text() or ""
            instrumento, tipo_inst = instrumento_da_pagina(i)
            paginas.append({
                "num": i + 1,           
                "texto": texto,
                "instrumento": instrumento,
                "tipo_instrumento": tipo_inst,
            })
    return paginas


def limpar_texto(texto: str) -> str:
    
    texto = re.sub(r"-\n", "", texto)         
    texto = re.sub(r"\n+", " ", texto)         
    texto = re.sub(r" {2,}", " ", texto)       
    texto = re.sub(r"\d+\s*OGIDÓC", "", texto) 
    return texto.strip()


def chunk_por_artigo(
    texto_completo: str,
    mapa_paginas: list[dict],
    max_chars: int = 2000
) -> list[dict]:
 

    
    pos_instrumento = []
    pos_atual = 0
    for pagina in mapa_paginas:
        texto_pag = limpar_texto(pagina["texto"])
        pos_instrumento.append((
            pos_atual,
            pos_atual + len(texto_pag),
            pagina["instrumento"],
            pagina["tipo_instrumento"],
            pagina["num"],
        ))
        pos_atual += len(texto_pag) + 1  

    def get_instrumento_por_pos(pos: int):
        for inicio, fim, nome, tipo, pg in pos_instrumento:
            if inicio <= pos < fim:
                return nome, tipo, pg
        return "Lei 8.078/1990", "lei", 1  

    
    padrao = r"(Art\.\s*\d+[\wº°]*[\s°º]*\.?)"
    partes = re.split(padrao, texto_completo)

    chunks = []
    pos_char = len(partes[0])  

    i = 1
    while i < len(partes) - 1:
        titulo = partes[i].strip()
        conteudo = partes[i + 1].strip()

        
        instrumento, tipo_inst, pagina_aprox = get_instrumento_por_pos(pos_char)

        pos_char += len(partes[i]) + len(partes[i + 1])

        if not conteudo or len(conteudo) < 100:
            i += 2
            continue

        metadados_base = {
            "artigo": titulo,
            "instrumento": instrumento,
            "tipo_instrumento": tipo_inst,
            "pagina_aprox": pagina_aprox,
            "fonte": "cdc-portugues-2013.pdf",
            "citacao": f"{instrumento}, {titulo}",
        }

        texto_chunk = f"{titulo} {conteudo}"

        if len(conteudo) <= max_chars:
            chunks.append({**metadados_base, "texto": texto_chunk, "tipo": "artigo_completo"})
        else:
        
            sub_partes = re.split(r"(§\s*\d+[°º]?|(?<!\w)[IVX]+\s*[-–])", conteudo)
            sub_chunk_atual = f"{titulo} {sub_partes[0]}"

            for j in range(1, len(sub_partes) - 1, 2):
                marcador = sub_partes[j]
                conteudo_sub = sub_partes[j + 1] if j + 1 < len(sub_partes) else ""
                candidato = f"{sub_chunk_atual} {marcador} {conteudo_sub}"

                if len(candidato) <= max_chars:
                    sub_chunk_atual = candidato
                else:
                    if sub_chunk_atual.strip():
                        chunks.append({
                            **metadados_base,
                            "texto": sub_chunk_atual.strip(),
                            "tipo": "artigo_parcial"
                        })
                    sub_chunk_atual = f"{titulo} (cont.) {marcador} {conteudo_sub}"

            if sub_chunk_atual.strip():
                chunks.append({
                    **metadados_base,
                    "texto": sub_chunk_atual.strip(),
                    "tipo": "artigo_parcial"
                })

        i += 2

    return chunks


def build_index():
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="intfloat/multilingual-e5-small"
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "..", "files", "cdc-portugues-2013.pdf")

    
    print("Extraindo texto do PDF por página")
    paginas = extrair_texto_por_pagina(pdf_path)
    print(f"  {len(paginas)} páginas extraídas")

    
    texto_completo = " ".join(limpar_texto(p["texto"]) for p in paginas)

    
    print("Chunkizando por artigo")
    chunks = chunk_por_artigo(texto_completo, paginas, max_chars=2000)
    print(f"  {len(chunks)} chunks gerados")

    
    from collections import Counter
    dist = Counter(c["instrumento"] for c in chunks)
    print("Distribuição por instrumento")
    for nome, qtd in dist.most_common():
        print(f"    {nome}: {qtd} chunks")

    
    nodes = []
    for idx, chunk in enumerate(chunks):
        node = TextNode(
            text=chunk["texto"],
            metadata={
                "artigo":           chunk["artigo"],
                "instrumento":      chunk["instrumento"],
                "tipo_instrumento": chunk["tipo_instrumento"],
                "tipo":             chunk["tipo"],
                "pagina_aprox":     chunk["pagina_aprox"],
                "citacao":          chunk["citacao"],
                "fonte":            chunk["fonte"],
                "chunk_id":         idx,
            }
        )
        nodes.append(node)
    print(f"\n  {len(nodes)} nodes criados com metadados")
    
    pc = create_index()
    pinecone_index = pc.Index("rag-cdc")
    print("Index Pinecone conectado")

    # 7. Cria vector store e indexa
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(nodes, storage_context=storage_context)
    print("Embeddings criados e enviados ao Pinecone com sucesso!")


build_index()