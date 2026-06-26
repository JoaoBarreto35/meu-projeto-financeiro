from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, BankAccount
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["artificial_intelligence"]
)

# Schema de validação do Pydantic para a frase que vem do React
class TextInput(BaseModel):
    text: str

@router.post("/parse-expense")
async def parse_expense_by_text(
    payload: TextInput, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        # Busca as contas do usuário logado para passar ao Gemini como contexto
        contas = db.query(BankAccount).filter(BankAccount.user_id == current_user.id).all()
        if not contas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Você precisa cadastrar pelo menos uma conta bancária antes de usar a IA."
            )

        # Instancia o serviço da IA passando a sessão do banco
        ai_service = AIService(db)
        
        # Chama o método do Gemini que já criamos no ai_service.py
        dados_estruturados = await ai_service.interpretar_gasto_texto(payload.text, contas)
        return dados_estruturados
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no motor de IA: {str(e)}")


@router.get("/insights")
async def get_ai_insights(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        ai_service = AIService(db)
        insights = await ai_service.gerar_insights_preditivos(current_user.id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar insights: {str(e)}")
