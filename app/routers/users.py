from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from firebase_admin import auth
from app.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import UserWithBirthdays

router = APIRouter()


# --------------------------------------------------
# AUTH DEPENDENCY (🔥 SINGLE SOURCE OF TRUTH)
# --------------------------------------------------

# --------------------------------------------------
# Explicit Sync Endpoint (OPTIONAL)
# --------------------------------------------------
@router.post("/sync", status_code=200)
def sync_user(
        user: User = Depends(get_current_user),
):
    return {
        "status": "ok",
        "firebase_uid": user.firebase_uid,
        "email": user.email,
    }


# --------------------------------------------------
# Get User (ADMIN / DEBUG)
# --------------------------------------------------
@router.get("/{firebase_uid}", response_model=UserWithBirthdays)
def get_user(firebase_uid: str, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.firebase_uid == firebase_uid)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
