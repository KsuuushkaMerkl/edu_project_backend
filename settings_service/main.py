from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings_service.endpoints import app as router


app = FastAPI(title="Settings Service", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/settings_service", tags=("Settings_service",))


@app.get("/")
def health():
    return {"status": "ok", "service": "settings"}