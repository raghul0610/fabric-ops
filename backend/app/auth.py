from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from supabase import Client, create_client

from app.config import get_settings
from app.db import get_db


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    role: str


def _client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)


def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        response = _client().auth.get_user(token)
        user = response.user
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return AuthenticatedUser(id=UUID(str(user.id)))


def require_authenticated_user(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    return user


def get_current_app_user(
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUser:
    row = db.execute(
        text("SELECT id, role FROM public.users WHERE id = :user_id"),
        {"user_id": str(user.id)},
    ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Application user is not provisioned",
        )

    return CurrentUser(id=UUID(str(row["id"])), role=str(row["role"]))


def require_role(*allowed_roles: str):
    def dependency(
        user: CurrentUser = Depends(get_current_app_user),
    ) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user

    return dependency
