from api.core.chat_engine import get_chat_engine
 

class AssistentService:
    @staticmethod
    def post_message(payload: str):
        chat_engine = get_chat_engine()
        
        response = chat_engine.chat(payload)
        
        
        return {"response": response.response}

    
    