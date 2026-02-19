from fastapi import APIRouter, Request, Depends
from mugeshbabu_agents.domain.auth.models import UserCreate, UserLogin, Token
from mugeshbabu_agents.domain.auth.service import auth_service
from mugeshbabu_agents.core.rate_limit import limiter

router = APIRouter()

@router.post("/signup", response_model=Token)
@limiter.limit("5/minute") # Max 5 signups per minute per IP
async def signup(request: Request, user: UserCreate):
    """Register a new user and return an access token."""
    return await auth_service.signup(user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login with email/password and return an access token."""
    return await auth_service.login(user)
