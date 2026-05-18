from pydantic import BaseModel


class InOutBase(BaseModel):
    message: str
    
    
class InOutRequest(InOutBase):
    pass


class InOutResponse(BaseModel):
    response: str
    