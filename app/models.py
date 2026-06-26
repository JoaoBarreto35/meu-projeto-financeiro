from sqlalchemy import Column, String, Float, Integer, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # checking, credit_card, etc.

class TransactionGroup(Base):
    __tablename__ = "transaction_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    total_installments = Column(Integer, nullable=False)
    is_recurring = Column(Boolean, default=False)

    # Relacionamento: Um grupo tem muitas transações (parcelas)
    transactions = relationship("Transaction", back_populates="group", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("transaction_groups.id"), nullable=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="pending")
    category = Column(String, default="Geral")
    installment_number = Column(Integer, default=1)

    group = relationship("TransactionGroup", back_populates="transactions")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
