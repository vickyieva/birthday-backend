from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter()


@router.post("/webhook")
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

    # Expected: /start recipient_12
    if text.startswith("/start recipient_"):
        try:
            recipient_id = int(text.split("_")[1])
        except ValueError:
            return {"ok": True}

        recipient = (
            db.query(models.Recipient)
            .filter(models.Recipient.id == recipient_id)
            .first()
        )

        if recipient:
            recipient.telegram_chat_id = chat_id
            db.commit()
            print(f"✅ Linked Telegram chat_id={chat_id} to recipient={recipient.id}")

    return {"ok": True}
