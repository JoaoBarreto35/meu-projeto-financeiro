from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BankAccount, User
from app.schemas import BankAccountCreate, BankAccountResponse
from app.dependencies import get_current_user
from typing import List
import uuid

router = APIRouter(
    prefix="/accounts",
    tags=["bank_accounts"]
)

@router.post("/", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: BankAccountCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        user_uuid = uuid.UUID(str(current_user.id))

        nova_conta = BankAccount(
            user_id=user_uuid,
            name=payload.name,
            type=payload.type
        )
        
        db.add(nova_conta)
        db.commit()
        db.refresh(nova_conta)
        
        return nova_conta
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro no Neon: {str(e)}")

@router.get("/", response_model=List[BankAccountResponse])
def list_accounts(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        user_uuid = uuid.UUID(str(current_user.id))
        
        # Busca no banco de dados Neon de forma síncrona e segura
        contas = db.query(BankAccount).filter(BankAccount.user_id == user_uuid).all()
        
        if contas is None:
            return []
            
        return contas
    except Exception as e:
        # Se falhar, retorna um array vazio para o React destravar o loading
        print(f"Erro ao buscar contas no Neon: {str(e)}")
        return []
