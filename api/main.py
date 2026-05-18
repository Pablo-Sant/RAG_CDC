from fastapi import FastAPI
from api.routes.assistent_route import router

app = FastAPI(
    title="Assistente Jurídico CDC",
    description="API com RAG baseada no Código de Defesa do Consumidor",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "API rodando"}