from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.routers import transactions, auth, accounts, ai
from app.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Governança Financeira com IA",
    description="Backend robusto integrado ao Neon.tech."
)

# 1. Liberamos o CORS padrão de forma agressiva para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Interceptor de Segurança Nativo (O segredo para matar o erro de Preflight)
@app.middleware("http")
async def interceptador_preflight_cors(request: Request, call_next):
    # Se o navegador enviar um OPTIONS, respondemos 200 OK na hora com as permissões
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
        return response
        
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(ai.router)
