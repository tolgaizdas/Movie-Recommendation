from fastapi import Header, HTTPException, Depends
import firebase_admin
from firebase_admin import auth, credentials
import os

# Initialize Firebase Admin SDK
import json

cred = None
firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")

try:
    if firebase_credentials:
        # Load from Environment Variable (JSON String)
        cred_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized with credentials from Environment.")
    elif os.path.exists("serviceAccountKey.json"):
        # Load from File (Local Dev)
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized with local serviceAccountKey.json.")
    else:
        # Fallback (Mock/ADC) - Verification will fail for real tokens without creds
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
            print("Warning: Firebase Admin initialized without explicit credentials.")
except Exception as e:
    print(f"Warning: Firebase Admin init failed: {e}")

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid header format")
    
    token = authorization.split("Bearer ")[1]
    
    # MOCK BYPASS FOR PROTOTYPE/TESTING
    # If the token is 'test-token', we allow it and return a dummy user
    if token == "test-token":
        return {"uid": "test_user", "email": "test@example.com"}

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Authentication Token")

def get_current_user(token_data: dict = Depends(verify_token)):
    return token_data
