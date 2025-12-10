from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from defects_service.endpoints import app as router


app = FastAPI(title="Defects Service", version="1.0.0")

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

app.include_router(router, prefix="/defects_service", tags=("Defects_service",))


@app.get("/")
def health():
    return {"status": "ok", "service": "defects"}