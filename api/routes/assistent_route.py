from fastapi import APIRouter
from api.schema.input_output_schema import InOutResponse, InOutRequest
from api.service.assistent_service import AssistentService
from fastapi import HTTPException

router = APIRouter()

@router.post('/assistent', response_model=InOutResponse, status_code=200)
def post_message(dto: InOutRequest):
    
    try:
        return AssistentService.post_message(dto.message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))