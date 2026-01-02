from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from firebase_admin import auth
from app.database import get_db
from app.models import User
from app.schemas import UserWithBirthdays

router = APIRouter()

def get_current_user(
        request: Request,
        db: Session = Depends(get_db),
):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    firebase_uid = decoded["uid"]
    email = decoded.get("email")

    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    # 🔥 AUTO-CREATE USER
    if not user:
        user = User(firebase_uid=firebase_uid, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


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

@router.get("/invite-link")
def invite_link():
    return {"ok": True}