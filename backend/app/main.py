from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .api import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="康复随访管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def init_data():
    from sqlalchemy.orm import Session
    from .models import User
    from .utils.auth import hash_password

    db = Session(bind=engine)
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                full_name="系统管理员"
            )
            db.add(admin)

        user = db.query(User).filter(User.username == "user").first()
        if not user:
            user = User(
                username="user",
                password_hash=hash_password("user123"),
                role="user",
                full_name="普通用户"
            )
            db.add(user)

        auditor = db.query(User).filter(User.username == "auditor").first()
        if not auditor:
            auditor = User(
                username="auditor",
                password_hash=hash_password("auditor123"),
                role="auditor",
                full_name="审计员"
            )
            db.add(auditor)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8032)
