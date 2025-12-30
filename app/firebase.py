import os
import json
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    if firebase_admin._apps:
        return

    # Railway / production
    json_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if json_env:
        cred_dict = json.loads(json_env)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return

    # Local development fallback
    local_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if local_path:
        cred = credentials.Certificate(local_path)
        firebase_admin.initialize_app(cred)
        return

    raise RuntimeError("Firebase credentials not found")

# 🔥 Initialize immediately
init_firebase()
