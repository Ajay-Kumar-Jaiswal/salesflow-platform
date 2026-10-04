from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse], summary="List all users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List system users (sales reps and admins) for assignments and management."""
    return AuthService.list_users(db)


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = AuthService.get_by_id(db, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="Update user (Admin only)")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin-only: update user information, password, or role."""
    return AuthService.update_user(db, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (Admin only)")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Admin-only: remove a user from the CRM."""
    AuthService.delete_user(db, user_id)
    return None
