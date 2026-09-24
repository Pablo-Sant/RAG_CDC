from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.assistent_route import router

app = FastAPI(
    title="Assistente Jurídico CDC",
    description="API com RAG baseada no Código de Defesa do Consumidor",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://assistente-cdc-front.calmplant-129c6d28.brazilsouth.azurecontainerapps.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "API rodando"}