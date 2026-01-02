from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter()


# @router.post("/webhook")
# async def telegram_webhook(
#         request: Request,
#         db: Session = Depends(get_db),
# ):
#     data = await request.json()
#
#     message = data.get("message")
#     if not message:
#         return {"ok": True}
#
#     text = message.get("text", "")
#     chat = message.get("chat", {})
#     chat_id = str(chat.get("id"))
#
#     # Expected: /start recipient_12
#     if text.startswith("/start recipient_"):
#         try:
#             recipient_id = int(text.split("_")[1])
#         except ValueError:
#             return {"ok": True}
#
#         recipient = (
#             db.query(models.Recipient)
#             .filter(models.Recipient.id == recipient_id)
#             .first()
#         )
#
#         if recipient:
#             recipient.telegram_chat_id = chat_id
#             db.commit()
#             print(f"✅ Linked Telegram chat_id={chat_id} to recipient={recipient.id}")
#     return {"ok": True}

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
    username = chat.get("username")
    first_name = chat.get("first_name", "Friend")

    # ---------------------------------
    # RECIPIENT-SPECIFIC LINK
    # ---------------------------------
    if text.startswith("/start recipient_"):
        recipient_id = int(text.replace("/start recipient_", ""))

        recipient = db.query(models.Recipient).filter_by(id=recipient_id).first()
        if not recipient:
            return {"ok": True}

        recipient.telegram_chat_id = chat_id
        recipient.telegram_username = username
        db.commit()

        send_telegram_message(
            chat_id,
            "✅ You are now connected! 🎉",
        )
        return {"ok": True}

    # ---------------------------------
    # USER INVITE LINK (FULL FLOW)
    # ---------------------------------
    if text.startswith("/start user_"):
        token = text.replace("/start user_", "").strip()

        user = db.query(models.User).filter_by(invite_token=token).first()
        if not user:
            return {"ok": True}

        # Check if recipient already exists
        recipient = (
            db.query(models.Recipient)
            .filter_by(telegram_chat_id=chat_id, user_id=user.id)
            .first()
        )

        if not recipient:
            recipient = models.Recipient(
                user_id=user.id,
                name=first_name,
                telegram_chat_id=chat_id,
                telegram_username=username,
            )
            db.add(recipient)
            db.commit()
            db.refresh(recipient)

        # Create / update session
        session = (
            db.query(models.TelegramSession)
            .filter_by(chat_id=chat_id)
            .first()
        )

        if not session:
            session = models.TelegramSession(
                chat_id=chat_id,
                user_id=user.id,
                recipient_id=recipient.id,
                step="ask_dob",
            )
            db.add(session)
        else:
            session.step = "ask_dob"

        db.commit()

        send_telegram_message(
            chat_id,
            "🎉 Hi! I’ll help collect details for birthday surprises.\n\n"
            "📅 What is your birthday? (Send as DD-MM, e.g. 14-08)",
        )
        return {"ok": True}
    # ---------------------------------
    # CONTINUATION FLOW
    # ---------------------------------
    session = db.query(models.TelegramSession).filter_by(chat_id=chat_id).first()
    if not session:
        return {"ok": True}

    recipient = db.query(models.Recipient).filter_by(id=session.recipient_id).first()
    if not recipient:
        return {"ok": True}

    # ---- ASK DOB ----
    if session.step == "ask_dob":
        try:
            day, month = map(int, text.split("-"))
            recipient.birth_day = day
            recipient.birth_month = month

            session.step = "ask_email"
            db.commit()

            send_telegram_message(
                chat_id,
                "📧 Would you like to add your email? (Send email or type skip)",
            )
        except:
            send_telegram_message(chat_id, "❌ Invalid format. Use DD-MM.")
        return {"ok": True}

    # ---- ASK EMAIL ----
    if session.step == "ask_email":
        if text.lower() != "skip":
            recipient.email = text.strip()

        session.step = "ask_phone"
        db.commit()

        send_telegram_message(
            chat_id,
            "📱 Would you like to add your phone number? (Send number or type skip)",
        )
        return {"ok": True}

    # ---- ASK PHONE ----
    if session.step == "ask_phone":
        if text.lower() != "skip":
            recipient.phone_number = text.strip()

        db.delete(session)
        db.commit()

        send_telegram_message(
            chat_id,
            "✅ All set! You’re now connected 🎉",
        )
        return {"ok": True}
