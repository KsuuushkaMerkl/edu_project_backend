import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth_service.model import Base, engine, SessionLocal, User
from auth_service.endpoints import app as router
from passlib.context import CryptContext

app = FastAPI(title="Auth Service", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(router,  prefix="/auth_service", tags=("auth_service",))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def create_initial_admin():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASS")

        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin_user = User(
                email=admin_email,
                name="Главный админ",
                role="admin",
                password_hash=pwd_context.hash(admin_password),
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok", "service": "auth"}