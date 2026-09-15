from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.assistent_route import router

app = FastAPI(
    title="Assistente Jurídico CDC",
    description="API com RAG baseada no Código de Defesa do Consumidor",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # ajuste pra porta do seu React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API rodando"} 