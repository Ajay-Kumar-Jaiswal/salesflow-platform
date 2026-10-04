from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email, name, password, and optional role."""
    return AuthService.register_user(db, user_in)


@router.post("/login", response_model=Token, summary="Log in with email and password")
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user credentials and issue a signed JWT access token."""
    user = AuthService.authenticate_user(db, login_in.email, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(token_data)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user")
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile and role information of the currently authenticated user."""
    return current_user
