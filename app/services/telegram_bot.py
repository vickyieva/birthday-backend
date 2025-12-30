from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()


@router.post("/telegram/webhook")
async def telegram_webhook(
        request: Request,
        db: Session = Depends(get_db),
):
    data = await request.json()

    message = data.get("message")
    if not message:
        return {"ok": True}

    text = message.get("text", "")
    chat = message.get("chat", {})
    chat_id = str(chat.get("id"))

    if text.startswith("/start recipient_"):
        recipient_id = int(text.split("_")[1])

        recipient = (
            db.query(models.Recipient)
            .filter(models.Recipient.id == recipient_id)
            .first()
        )

        if recipient:
            recipient.telegram_chat_id = chat_id
            db.commit()

    return {"ok": True}
