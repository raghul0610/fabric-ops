from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWKClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    role: str


def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    settings = get_settings()
    issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
    jwks_url = f"{issuer}/.well-known/jwks.json"

    try:
        signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    try:
        return AuthenticatedUser(id=UUID(str(user_id)))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc


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
