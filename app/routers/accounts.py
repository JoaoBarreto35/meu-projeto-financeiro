from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BankAccount, User
from app.schemas import BankAccountCreate, BankAccountResponse
from app.dependencies import get_current_user
from typing import List

router = APIRouter(
    prefix="/accounts",
    tags=["bank_accounts"]
)

@router.post("/", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: BankAccountCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        # Cria a instância do SQLAlchemy com os dados que vieram do React
        nova_conta = BankAccount(
            user_id=current_user.id,
            name=payload.name,
            type=payload.type
        )
        
        # Insere e salva de verdade no banco Neon
        db.add(nova_conta)
        db.commit()
        db.refresh(nova_conta) # Atualiza o objeto para pegar o ID gerado pelo banco
        
        return nova_conta
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[BankAccountResponse])
async def list_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Retorna apenas as contas e cartões criados pelo usuário logado
        contas = db.query(BankAccount).filter(BankAccount.user_id == current_user.id).all()
        
        # Se não houver contas cadastradas, retorna uma lista vazia de forma segura
        if not contas:
            return []
            
        return contas
    except Exception as e:
        # Evita o erro 500 e exibe o log real do banco de dados no console
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erro ao acessar banco de dados: {str(e)}"
        )
    
