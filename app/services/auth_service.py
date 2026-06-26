import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Transforma a senha limpa em um hash seguro usando bcrypt puro."""
        # Transforma a senha em bytes
        pwd_bytes = password.encode('utf-8')
        # Gera o salt (o tempero de segurança da senha)
        salt = bcrypt.gensalt()
        # Faz o hash e decodifica de volta para salvar como texto no Neon
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compara a senha digitada pelo usuário com o hash salvo no banco."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=8)) -> str:
        """Gera o token JWT assinado digitalmente."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
        return encoded_jwt
