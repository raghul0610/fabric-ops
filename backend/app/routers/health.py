from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["system"])

@router.get("")
def health() -> dict[str, str]:
    return {"status": "ok"}
