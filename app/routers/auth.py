from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    # Verifica se o e-mail já existe no banco Neon
    user_exists = db.query(User).filter(User.email == payload.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este e-mail já está cadastrado."
        )
    
    # Cria o novo usuário com a senha criptografada
    hashed_pwd = AuthService.hash_password(payload.password)
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    
    return {"status": "sucesso", "mensagem": "Usuário criado com sucesso!"}

@router.post("/login", response_model=TokenResponse)
async def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not AuthService.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Se a senha estiver correta, gera o crachá (Token) contendo o ID dele
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = AuthService.create_access_token(data=token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}
