from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional


# -------------------------
# USER SCHEMAS
# -------------------------

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    firebase_uid: str


class UserResponse(UserBase):
    id: int
    firebase_uid: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# BIRTHDAY SCHEMAS
# -------------------------

class BirthdayBase(BaseModel):
    name: str
    birth_date: date
    channel: str = "telegram"
    message: Optional[str] = None


class BirthdayCreate(BaseModel):
    name: str
    birth_date: date
    channel: str
    message: Optional[str] = None
    recipient_id: int   # ✅ REQUIRED


# -------------------------
# BIRTHDAY SCHEMAS
# -------------------------

class BirthdayResponse(BirthdayBase):
    id: int
    is_active: bool
    created_at: datetime
    last_sent: Optional[datetime] = None   # ✅ FIXED

    class Config:
        from_attributes = True


# -------------------------
# USER WITH BIRTHDAYS
# -------------------------

class UserWithBirthdays(UserResponse):
    birthdays: List[BirthdayResponse] = []


class RecipientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class RecipientResponse(BaseModel):
    id: int
    name: str
    telegram_chat_id: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    created_at: datetime   # ✅ FIXED

    class Config:
        from_attributes = True
