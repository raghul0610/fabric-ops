from fastapi import FastAPI

from app.routers.events import router as events_router
from app.routers.health import router as health_router
from app.routers.teams import router as teams_router


app = FastAPI(title="FABRIC Ops API", version="0.1.0")
app.include_router(health_router)
app.include_router(events_router)
app.include_router(teams_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"service": "fabric-ops-api", "status": "ok"}
