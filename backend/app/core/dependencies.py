from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import AuthService

security_bearer = HTTPBearer(auto_error=False)


def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract user if valid Bearer token provided, otherwise return None."""
    if not auth or not auth.credentials:
        return None

    payload = decode_access_token(auth.credentials)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return AuthService.get_by_id(db, int(user_id))


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Enforce authentication on protected endpoints."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or are invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce ADMIN role on restricted endpoints."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to perform this action"
        )
    return current_user
