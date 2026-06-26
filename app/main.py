from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importe o Middleware
from app.routers import accounts, transactions, auth
from app.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Governança Financeira com IA",
    description="Backend robusto integrado ao Neon.tech."
)

# ─── CONFIGURAÇÃO DO CORS ──────────────────────────────────────────
# Lista de URLs de onde as requisições podem vir
origins = [
    "http://localhost:3000",     # Seu React local tradicional
    "http://localhost:5173",     # Se você usar React com Vite local
    "http://localhost:5174",     # Se você usar React com Vite local
    "https://vitejsviteq2uakyyn-slia--5173--29a3b5f7.local-corp.webcontainer.io",     # Se você usar React com Vite stackblitz
    "https://vercel.app",  # URL de produção do seu React no futuro
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Permite requisições destas origens
    allow_credentials=True,           # Permite envio de cookies/tokens de autenticação
    allow_methods=["*"],              # Permite todos os métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],              # Permite todos os cabeçalhos de requisição
)
# ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"status": "API conectada ao Neon.tech com CORS liberado!"}
