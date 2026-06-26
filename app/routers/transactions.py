from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import TransactionGroupCreate
from app.services.finance_service import FinanceService
from app.database import get_db
from app.dependencies import get_current_user # Importe o guarda
from app.models import User # Importe o modelo de Usuário

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.post("/new-expense")
async def create_expense(
    payload: TransactionGroupCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Agora a rota exige login!
):
    try:
        finance_service = FinanceService(db)
        # Usamos o ID do usuário real que veio de dentro do Token JWT decodificado
        resultado = await finance_service.cadastrar_gasto_parcelado(payload, current_user.id)
        return {"status": "sucesso", "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Adicione estas importações no topo do app/routers/transactions.py se não houver
from typing import List
from datetime import date
from app.models import Transaction
from sqlalchemy import extract

# ... mantenha sua rota @router.post("/new-expense") existente aqui ...

@router.get("/monthly-statement")
async def get_monthly_statement(
    month: int, 
    year: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todas as transações (incluindo parcelas) de um mês e ano específicos.
    Perfeito para alimentar os gráficos do React.
    """
    transacoes = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.due_date) == month,
        extract('year', Transaction.due_date) == year
    ).order_by(Transaction.due_date.asc()).all()
    
    # Calcula o resumo do mês dinamicamente no backend
    total_gasto = sum(t.amount for t in transacoes if t.amount < 0)
    total_recebido = sum(t.amount for t in transacoes if t.amount > 0)
    
    return {
        "mes_referencia": f"{month:02d}/{year}",
        "resumo": {
            "total_despesas": round(total_gasto, 2),
            "total_receitas": round(total_recebido, 2),
            "saldo_final": round(total_recebido + total_gasto, 2)
        },
        "transacoes": [
            {
                "id": str(t.id),
                "account_id": str(t.account_id),
                "group_id": str(t.group_id) if t.group_id else None,
                "description": t.description,
                "amount": t.amount,
                "due_date": t.due_date.isoformat(),
                "status": t.status,
                "category": t.category,
                "installment_number": t.installment_number
            } for t in transacoes
        ]
    }
