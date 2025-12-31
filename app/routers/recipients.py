# app/routers/recipients.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.routers.users import get_current_user
from app import models, schemas
from app.models import User

router = APIRouter()


# ---------------------------
# CREATE RECIPIENT
# ---------------------------
@router.post("/", response_model=schemas.RecipientResponse)
def create_recipient(
        data: schemas.RecipientCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    recipient = models.Recipient(
        user_id=user.id,   # ✅ FIX
        name=data.name,
        email=data.email,
        phone_number=data.phone_number,
        telegram_chat_id=data.telegram_chat_id,
    )

    db.add(recipient)
    db.commit()
    db.refresh(recipient)

    return recipient


# ---------------------------
# LIST RECIPIENTS
# ---------------------------
@router.get("/", response_model=List[schemas.RecipientResponse])
def list_recipients(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return (
        db.query(models.Recipient)
        .filter(models.Recipient.user_id == user.id)  # ✅ FIX
        .all()
    )
