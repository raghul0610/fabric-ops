from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers.ai_reviews import router as ai_reviews_router
from app.routers.events import router as events_router
from app.routers.health import router as health_router
from app.routers.submissions import router as submissions_router
from app.routers.tasks import router as tasks_router
from app.routers.teams import router as teams_router


settings = get_settings()

app = FastAPI(title="FABRIC Ops API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(teams_router)
app.include_router(submissions_router)
app.include_router(ai_reviews_router)
app.include_router(tasks_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"service": "fabric-ops-api", "status": "ok"}
