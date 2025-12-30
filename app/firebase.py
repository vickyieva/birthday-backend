import firebase_admin
from firebase_admin import credentials, auth
import json
import os

if not firebase_admin._apps:
    cred_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    cred = credentials.Certificate(json.loads(cred_json))
    firebase_admin.initialize_app(cred)

def verify_token(token: str):
    """
    Verifies Firebase ID token and returns decoded payload
    """
    return auth.verify_id_token(token)
