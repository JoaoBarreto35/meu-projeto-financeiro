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
    "https://vitejsviteq2uakyyn-slia--5173--29a3b5f7.local-corp.webcontainer.io",
    "https://vitejsviteq2uakyyn-slia--5173--29a3b5f7.local-corp.webcontainer.io/*"     # Se você usar React com Vite stackblitz
    "https://vercel.app",  # URL de produção do seu React no futuro
]

# Abra app/main.py e ajuste esta seção:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Força a liberação para qualquer origem de teste!
    allow_credentials=False,         # Importante: mude para False se usar "*" no allow_origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"status": "API conectada ao Neon.tech com CORS liberado!"}
