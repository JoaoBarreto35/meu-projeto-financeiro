from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class TransactionGroupCreate(BaseModel):
    description: str
    total_amount: float
    total_installments: int
    account_id: str
    category: Optional[str] = "Geral"
    is_recurring: bool = False

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class BankAccountCreate(BaseModel):
    name: str
    type: str  # 'checking_account', 'credit_card', 'savings'

class BankAccountResponse(BaseModel):
    id: UUID       # Mudado de str para UUID!
    user_id: UUID  # Garante que o ID do usuário também converta sem quebrar
    name: str
    type: str

    class Config:
        from_attributes = True  # Permite ler objetos do SQLAlchemy diretamente
