from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
import firebase_admin
from app.services.telegram_bot import router as telegram_router
from app.routers.users import router as users_router, get_current_user
from app.routers.birthdays import router as birthdays_router
from app.scheduler import start_scheduler
from app.database import Base, engine
from app import models
from app.routers.recipients import router as recipients_router

import json
import os

if not firebase_admin._apps:
    json_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if json_env:
        cred_dict = json.loads(json_env)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    # Local development fallback
    local_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if local_path:
        cred = credentials.Certificate(local_path)
        firebase_admin.initialize_app(cred)


app = FastAPI(
    title="Birthday Auto Wisher API",
    version="1.0.0",
)

# 🗄️ Database
Base.metadata.create_all(bind=engine)

# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧪 AUTH TEST
@app.get("/auth-test")
def auth_test(user=Depends(get_current_user)):
    return user

# 📌 ROUTERS (PREFIX ONLY HERE)
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(birthdays_router, prefix="/birthdays", tags=["Birthdays"])
app.include_router(recipients_router, prefix="/recipients", tags=["Recipients"])
app.include_router(telegram_router, prefix="/telegram", tags=["Telegram"])

# ⏰ Scheduler
@app.on_event("startup")
async def startup_event():
    start_scheduler()

# ❤️ Health
@app.get("/")
def root():
    return {"status": "ok", "message": "Birthday Auto Wisher API running"}

@app.get("/__routes")
def show_routes():
    return [route.path for route in app.router.routes]
