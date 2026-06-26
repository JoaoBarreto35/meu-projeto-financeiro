from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Aqui você coloca qualquer URL de banco de dados (Neon, Render, Supabase, etc.)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

# O engine é o motor que gerencia a comunicação real com o banco
engine = create_engine(DATABASE_URL)

# Cada requisição terá sua própria sessão de banco isolada
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que nossos modelos em POO vão herdar para criar as tabelas
Base = declarative_base()

# Função utilitária (Dependency Injection) para abrir e fechar a conexão por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
