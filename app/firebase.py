import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase ONCE
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/user/StudioProjects/birthday_wisher/backend/"
        "birthday-auto-wisher-firebase-adminsdk-fbsvc-7e41082a44.json"
    )
    firebase_admin.initialize_app(cred)


def verify_token(token: str):
    """
    Verifies Firebase ID token and returns decoded payload
    """
    return auth.verify_id_token(token)
