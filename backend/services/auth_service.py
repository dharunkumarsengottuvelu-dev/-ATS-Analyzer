from sqlalchemy.orm import Session
from backend.repositories.user_repository import user_repository
from backend.core.security import verify_password, get_password_hash, create_access_token
from backend.core.exceptions import UnauthorizedException, BadRequestException

class AuthService:
    def authenticate_user(self, db: Session, username: str, password: str):
        user = user_repository.get_by_username(db, username=username)
        if not user:
            raise UnauthorizedException("Incorrect username or password")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect username or password")
        return user
        
    def register_user(self, db: Session, username: str, email: str, password: str):
        if user_repository.get_by_username(db, username=username):
            raise BadRequestException("Username already registered")
        if user_repository.get_by_email(db, email=email):
            raise BadRequestException("Email already registered")
            
        hashed_password = get_password_hash(password)
        user_in = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password
        }
        return user_repository.create(db=db, obj_in=user_in)

auth_service = AuthService()
