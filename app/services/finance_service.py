from sqlalchemy.orm import Session
from app.models import TransactionGroup, Transaction
from app.schemas import TransactionGroupCreate
from datetime import date
import uuid

class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    async def cadastrar_gasto_parcelado(self, payload: TransactionGroupCreate, user_id: uuid.UUID):
        # 1. Cria a instância do Grupo (Compra Mãe) usando o Modelo do SQLAlchemy
        novo_grupo = TransactionGroup(
            user_id=user_id,
            description=payload.description,
            total_amount=payload.total_amount,
            total_installments=payload.total_installments,
            is_recurring=payload.is_recurring
        )
        
        # Adiciona na sessão do banco
        self.db.add(novo_grupo)
        self.db.flush() # Faz o banco gerar o ID do grupo temporariamente sem salvar definitivo ainda

        # 2. Gera as parcelas individuais
        valor_parcela = payload.total_amount / payload.total_installments
        data_base = date.today()

        for i in range(1, payload.total_installments + 1):
            ano = data_base.year + (data_base.month + i - 2) // 12
            mes = (data_base.month + i - 2) % 12 + 1
            data_vencimento = date(ano, mes, data_base.day)

            nova_parcela = Transaction(
                user_id=user_id,
                account_id=uuid.UUID(payload.account_id),
                group_id=novo_grupo.id,
                description=f"{payload.description} ({i}/{payload.total_installments})",
                amount=-abs(valor_parcela),
                due_date=data_vencimento,
                status="pending",
                category=payload.category,
                installment_number=i
            )
            self.db.add(nova_parcela)

        # 3. Salva tudo de uma vez no banco de dados (Commit de transação segura)
        self.db.commit()

        return {
            "grupo_id": str(novo_grupo.id),
            "total_parcelas": payload.total_installments
        }
