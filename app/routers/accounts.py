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
async def create_account(
    payload: BankAccountCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        # Converte explicitamente a string do ID para o objeto UUID do banco
        user_uuid = uuid.UUID(str(current_user.id))

        # Cria a instância do SQLAlchemy mapeada
        nova_conta = BankAccount(
            user_id=user_uuid,  # Corrigido aqui!
            name=payload.name,
            type=payload.type
        )
        
        # Insere e salva no banco Neon
        db.add(nova_conta)
        db.commit()
        db.refresh(nova_conta)
        
        return nova_conta
    except Exception as e:
        db.rollback()
        # Captura e envia o erro real para o React em vez de morrer em 500
        raise HTTPException(status_code=400, detail=f"Erro no Neon: {str(e)}")


@router.get("/", response_model=List[BankAccountResponse])
async def list_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        user_uuid = uuid.UUID(str(current_user.id))
        
        # Filtra as contas do Neon pelo UUID correto
        contas = db.query(BankAccount).filter(BankAccount.user_id == user_uuid).all()
        
        return contas
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro analítico no banco: {str(e)}"
        )


