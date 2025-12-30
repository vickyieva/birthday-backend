# app/models.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    firebase_uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True)

    birthdays = relationship(
        "Birthday",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    recipients = relationship(
        "Recipient",
        back_populates="user",
        cascade="all, delete-orphan",
    )



class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="recipients",
    )

    created_at = Column(DateTime, default=datetime.utcnow)



class Birthday(Base):
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    channel = Column(String, nullable=False)
    message = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sent = Column(DateTime, nullable=True)

    # 🔥 THIS WAS MISSING OR BROKEN
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ✅ BACK-REFERENCE
    user = relationship("User", back_populates="birthdays")

    recipient_id = Column(
        Integer,
        ForeignKey("recipients.id", ondelete="CASCADE"),
        nullable=False,
    )

    recipient = relationship("Recipient")

