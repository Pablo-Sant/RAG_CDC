from api.core.chat_engine import get_chat_engine
 

class AssistentService:
    @staticmethod
    def post_message(payload: str):
        chat_engine = get_chat_engine()
        
        response = chat_engine.chat(payload)
        
        chunks_usados = [
            {
                "texto": node.text,
                "score": node.score,
                "fonte": node.metadata.get("file_name"),
                "pagina": node.metadata.get("page_label")
            }
            
            for node in response.source_nodes
        ]
        
        return {
            
            "response": response.response,
            "chunks_usados": chunks_usados
            
            }