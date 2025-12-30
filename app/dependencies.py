from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from firebase_admin import auth

from app.database import get_db
from app.models import User


def get_current_user(
        request: Request,
        db: Session = Depends(get_db),
):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    firebase_uid = decoded["uid"]

    user = (
        db.query(User)
        .filter(User.firebase_uid == firebase_uid)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    return user  # ✅ ALWAYS SQLALCHEMY USER
