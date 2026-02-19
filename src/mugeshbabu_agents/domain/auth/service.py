import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from mugeshbabu_agents.core.config import settings
from mugeshbabu_agents.infrastructure.db import db_manager
from mugeshbabu_agents.domain.auth.models import User, UserCreate, UserLogin, Token, UserRepository

# Password Context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def __init__(self):
        # We'll initialize repository on demand
        pass

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.auth.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.auth.jwt_secret, algorithm=settings.auth.jwt_algorithm)
        return encoded_jwt

    async def signup(self, user_in: UserCreate) -> Token:
        db = db_manager.get_master_db()
        repo = UserRepository(db, "users", User)

        # 1. Check if user exists
        existing_user = await repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 2. Create User
        hashed_password = self.get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_password
        )
        await repo.create(new_user)

        # 3. Create Token
        access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(new_user.id), "email": new_user.email}, # Store ID and email in token
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")

    async def login(self, user_in: UserLogin) -> Token:
        db = db_manager.get_master_db()
        repo = UserRepository(db, "users", User)

        # 1. Authenticate User
        user = await repo.get_by_email(user_in.email)
        if not user or not self.verify_password(user_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Create Token
        access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")

auth_service = AuthService()
