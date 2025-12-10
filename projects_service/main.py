from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from projects_service.endpoints import app as router


app = FastAPI(title="Projects Service", version="1.0.0")

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


app.include_router(router, prefix="/projects_service", tags=("rojects_service",))


@app.get("/")
def health():
    return {"status": "ok", "service": "projects"}