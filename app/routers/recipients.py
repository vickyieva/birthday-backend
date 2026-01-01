from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.user import get_current_user
from app.models import Recipient, User
from app.schemas import RecipientCreate, RecipientResponse

router = APIRouter()


# --------------------------------------------------
# TELEGRAM INVITE LINK BUILDER
# --------------------------------------------------
def telegram_invite_link(recipient_id: int) -> str:
    """
    Generates a Telegram deep link that binds
    a Telegram chat to a recipient record.
    """
    BOT_USERNAME = "YOUR_BOT_USERNAME"  # 👈 replace once
    return f"https://t.me/{BOT_USERNAME}?start=recipient_{recipient_id}"


# --------------------------------------------------
# CREATE RECIPIENT
# --------------------------------------------------
@router.post("/", response_model=RecipientResponse)
def create_recipient(
        data: RecipientCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    recipient = Recipient(
        user_id=user.id,
        name=data.name,
        email=data.email,
        phone_number=data.phone_number,
        telegram_chat_id=None,  # linked later via bot
    )

    db.add(recipient)
    db.commit()
    db.refresh(recipient)

    return {
        "id": recipient.id,
        "name": recipient.name,
        "email": recipient.email,
        "phone_number": recipient.phone_number,
        "telegram_chat_id": recipient.telegram_chat_id,
        "created_at": recipient.created_at,
        "telegram_link": telegram_invite_link(recipient.id),
    }


# --------------------------------------------------
# LIST RECIPIENTS (FOR CURRENT USER)
# --------------------------------------------------
@router.get("/", response_model=List[RecipientResponse])
def list_recipients(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    recipients = (
        db.query(Recipient)
        .filter(Recipient.user_id == user.id)
        .order_by(Recipient.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "phone_number": r.phone_number,
            "telegram_chat_id": r.telegram_chat_id,
            "created_at": r.created_at,
            "telegram_link": telegram_invite_link(r.id),
        }
        for r in recipients
    ]


# --------------------------------------------------
# DELETE RECIPIENT
# --------------------------------------------------
@router.delete("/{recipient_id}")
def delete_recipient(
        recipient_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    recipient = (
        db.query(Recipient)
        .filter(
            Recipient.id == recipient_id,
            Recipient.user_id == user.id,
            )
        .first()
    )

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    db.delete(recipient)
    db.commit()

    return {"status": "deleted"}
