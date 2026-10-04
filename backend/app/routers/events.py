from fastapi import APIRouter, Depends
from app.auth import AuthenticatedUser, require_authenticated_user

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/me")
def events_for_current_user(
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, str]:
    return {"user_id": str(user.id)}
