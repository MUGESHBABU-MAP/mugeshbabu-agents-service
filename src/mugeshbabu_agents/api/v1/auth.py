from fastapi import APIRouter
from mugeshbabu_agents.domain.auth.models import UserCreate, UserLogin, Token
from mugeshbabu_agents.domain.auth.service import auth_service

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    """Register a new user and return an access token."""
    return await auth_service.signup(user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login with email/password and return an access token."""
    return await auth_service.login(user)
