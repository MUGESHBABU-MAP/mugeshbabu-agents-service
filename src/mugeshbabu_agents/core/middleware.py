from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import re

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, public_paths: list[str] = None):
        super().__init__(app)
        self.public_paths = public_paths or []
        # Compile regex for public paths to handle wildcards or specific patterns if needed
        # For now, exact match or simple prefix checking is sufficient.
        
        # Adding standard public paths
        self.public_paths.extend([
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/auth" # Login and Signup must be public
        ])

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Check if path is public
        if any(path.startswith(p) for p in self.public_paths):
            return await call_next(request)

        # 1. Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing Authorization header"}
            )

        # 2. Validate Bearer token format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid credentials scheme")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Authorization header format. Expected 'Bearer <token>'"}
            )

        # 3. Verify Token
        try:
            from mugeshbabu_agents.core.config import settings
            import jwt
            
            payload = jwt.decode(
                token, 
                settings.auth.jwt_secret, 
                algorithms=[settings.auth.jwt_algorithm]
            )
            # Inject user info into request state
            request.state.user = payload
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"}
            )
        except jwt.PyJWTError as e:
            logger.error(f"JWT Verification Failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Could not validate credentials"}
            )
            
        return await call_next(request)
