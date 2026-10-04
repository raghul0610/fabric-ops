from fastapi import APIRouter, Depends

from app.auth import CurrentUser, require_role

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/me")
def events_for_current_user(
    user: CurrentUser = Depends(require_role("ADMIN", "LEAD", "MEMBER")),
) -> dict[str, str]:
    return {"user_id": str(user.id), "role": user.role}
