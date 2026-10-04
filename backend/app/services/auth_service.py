from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        clean_email = user_in.email.lower().strip()
        existing = AuthService.get_by_email(db, clean_email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            name=user_in.name.strip(),
            email=clean_email,
            hashed_password=hashed_password,
            role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        clean_email = email.lower().strip()
        user = AuthService.get_by_email(db, clean_email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def list_users(db: Session) -> List[User]:
        return db.query(User).order_by(User.name.asc()).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
        user = AuthService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        if user_in.email is not None:
            clean_email = user_in.email.lower().strip()
            existing = AuthService.get_by_email(db, clean_email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use by another account"
                )
            user.email = clean_email

        if user_in.name is not None:
            user.name = user_in.name.strip()

        if user_in.password is not None and user_in.password.strip():
            user.hashed_password = get_password_hash(user_in.password)

        if user_in.role is not None:
            user.role = user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = AuthService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        db.delete(user)
        db.commit()
        return True
