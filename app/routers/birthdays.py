from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.routers.users import get_current_user
from app.models import Birthday, User
from app.schemas import BirthdayCreate, BirthdayResponse

router = APIRouter()

# ---------------------------
# CREATE BIRTHDAY
# ---------------------------
@router.post("/", response_model=BirthdayResponse)
def create_birthday(
        birthday: BirthdayCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    new_birthday = Birthday(
        name=birthday.name,
        birth_date=birthday.birth_date,
        channel=birthday.channel,
        message=birthday.message,
        user_id=user.id,
    )

    db.add(new_birthday)
    db.commit()
    db.refresh(new_birthday)

    return new_birthday


# ---------------------------
# DASHBOARD — UNSENT ONLY
# ---------------------------
@router.get("/", response_model=List[BirthdayResponse])
def list_pending_birthdays(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return (
        db.query(Birthday)
        .filter(
            Birthday.user_id == user.id,
            Birthday.is_active == True,
            Birthday.last_sent.is_(None),
            )
        .all()
    )


# ---------------------------
# SENT BIRTHDAYS
# ---------------------------
@router.get("/sent")
def list_sent_birthdays(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    birthdays = (
        db.query(Birthday)
        .filter(
            Birthday.user_id == user.id,
            Birthday.is_active == True,
            Birthday.last_sent.isnot(None),
            )
        .all()
    )

    return [
        {
            "id": b.id,
            "name": b.name,
            "birth_date": b.birth_date.isoformat(),
            "channel": b.channel,
            "message": b.message,
            "is_active": b.is_active,
            "created_at": b.created_at.isoformat(),
            "last_sent": b.last_sent.isoformat() if b.last_sent else None,
        }
        for b in birthdays
    ]


# ---------------------------
# UPDATE BIRTHDAY
# ---------------------------
@router.put("/{birthday_id}", response_model=BirthdayResponse)
def update_birthday(
        birthday_id: int,
        birthday: BirthdayCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    existing = (
        db.query(Birthday)
        .filter(Birthday.id == birthday_id, Birthday.user_id == user.id)
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Birthday not found")

    existing.name = birthday.name
    existing.birth_date = birthday.birth_date
    existing.channel = birthday.channel
    existing.message = birthday.message

    db.commit()
    db.refresh(existing)

    return existing


# ---------------------------
# DELETE BIRTHDAY
# ---------------------------
@router.delete("/{birthday_id}")
def delete_birthday(
        birthday_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    birthday = (
        db.query(Birthday)
        .filter(Birthday.id == birthday_id, Birthday.user_id == user.id)
        .first()
    )

    if not birthday:
        raise HTTPException(status_code=404, detail="Birthday not found")

    db.delete(birthday)
    db.commit()

    return {"status": "deleted"}


# ---------------------------
# RUN SCHEDULER (TEST)
# ---------------------------
@router.post("/run-scheduler")
def run_scheduler_test(user=Depends(get_current_user)):
    from app.scheduler import birthday_job
    birthday_job()
    return {"status": "scheduler executed"}


# ---------------------------
# RESEND
# ---------------------------
from datetime import datetime, timedelta

@router.post("/{birthday_id}/resend")
def resend_birthday(
        birthday_id: int,
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    birthday = (
        db.query(Birthday)
        .filter(
            Birthday.id == birthday_id,
            Birthday.user_id == user.id,
            Birthday.is_active == True,
            )
        .first()
    )

    if not birthday:
        raise HTTPException(status_code=404, detail="Birthday not found")

    if birthday.last_sent:
        elapsed = datetime.utcnow() - birthday.last_sent
        if elapsed < timedelta(minutes=5):
            raise HTTPException(
                status_code=429,
                detail="Please wait before resending",
            )

    from app.scheduler import send_birthday_message
    send_birthday_message(birthday)

    birthday.last_sent = datetime.utcnow()
    db.commit()
    db.refresh(birthday)

    return {
        "status": "resent",
        "last_sent": birthday.last_sent.isoformat(),
    }
