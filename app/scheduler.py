from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Birthday
from app.services.telegram import send_telegram_message
from app.services.email import send_email
from app.services.sms import send_sms


# --------------------------------------------------
# MESSAGE BUILDER
# --------------------------------------------------
def build_message(name: str, style: str, sender: str) -> str:
    if style == "formal":
        body = (
            "Wishing you a wonderful year filled with joy, "
            "success, and good health 🎂"
        )
    elif style == "funny":
        body = "Eat cake, make a wish, and don’t count the candles 😄🎂"
    elif style == "romantic":
        body = "May your day be filled with love and beautiful moments 💖"
    else:
        body = "Wishing you a fantastic birthday 🎉"

    return (
        f"🎉 Happy Birthday {name}!\n\n"
        f"{body}\n\n"
        f"— Sent by {sender}"
    )


# --------------------------------------------------
# SEND MESSAGE (CHANNEL AWARE)
# --------------------------------------------------
def send_birthday_message(birthday: Birthday):
    recipient = birthday.recipient
    sender = birthday.user.email.split("@")[0] if birthday.user.email else "Your Friend"

    message = build_message(
        name=recipient.name,
        style=birthday.message or "formal",
        sender=sender,
    )

    if birthday.channel == "telegram" and recipient.telegram_chat_id:
        send_telegram_message(
            chat_id=recipient.telegram_chat_id,
            text=message,
        )

    elif birthday.channel == "email" and recipient.email:
        send_email(recipient.email, message)

    elif birthday.channel == "sms" and recipient.phone_number:
        send_sms(recipient.phone_number, message)

    else:
        print(
            f"⚠️ Skipped sending for birthday_id={birthday.id} "
            f"(missing contact for channel={birthday.channel})"
        )


# --------------------------------------------------
# DAILY JOB
# --------------------------------------------------
def birthday_job():
    db: Session = SessionLocal()
    today = date.today()

    try:
        birthdays = (
            db.query(Birthday)
            .filter(
                Birthday.is_active == True,
                Birthday.last_sent.is_(None),
                Birthday.recipient_id.isnot(None),  # 🔥 CRITICAL
                func.strftime("%m-%d", Birthday.birth_date)
                == today.strftime("%m-%d"),
                )
            .all()
        )

        print(f"🎯 MATCHED BIRTHDAYS: {len(birthdays)}")

        sent_count = 0

        for birthday in birthdays:
            recipient = birthday.recipient

            if not recipient:
                print(f"⚠️ Birthday {birthday.id} has no recipient")
                continue

            # Check channel availability BEFORE sending
            if birthday.channel == "telegram" and not recipient.telegram_chat_id:
                print(f"⚠️ Recipient {recipient.id} has no telegram_chat_id")
                continue

            if birthday.channel == "email" and not recipient.email:
                print(f"⚠️ Recipient {recipient.id} has no email")
                continue

            if birthday.channel == "sms" and not recipient.phone_number:
                print(f"⚠️ Recipient {recipient.id} has no phone number")
                continue

            # ✅ Send
            send_birthday_message(birthday)

            # ✅ Mark as sent ONLY if message was actually sent
            birthday.last_sent = datetime.utcnow()
            db.add(birthday)
            sent_count += 1

            print(f"✅ SENT: {birthday.name}")

        db.commit()

        if sent_count == 0:
            print("ℹ️ No messages sent (missing contacts or recipients)")
        else:
            print(f"✅ Successfully sent {sent_count} birthday message(s)")

    except Exception as e:
        db.rollback()
        print("❌ Scheduler error:", str(e))

    finally:
        db.close()


# --------------------------------------------------
# SCHEDULER BOOTSTRAP
# --------------------------------------------------
def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        birthday_job,
        trigger="cron",
        hour=7,
        minute=0,
        id="birthday_job",
        replace_existing=True,
    )

    scheduler.start()
    print("⏰ Scheduler started (runs daily at 07:00 UTC)")
