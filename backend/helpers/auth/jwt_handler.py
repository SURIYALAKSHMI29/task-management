import jwt
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import time
from pydantic import EmailStr

# reference: https://testdriven.io/blog/fastapi-jwt-auth/#jwt-authentication

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def create_jwt_token(user_email: EmailStr):
    payload = {
        "user_email": user_email,
        "exp": int(time.time()) + (3600*24)   # one day
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer"            
    }


def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError as e:
        print("ExpiredSignatureError:", e)
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print("InvalidTokenError:", e)
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("Other JWT decode error:", e)  # <-- catch-all for any other JWT issues
        raise HTTPException(status_code=401, detail="Invalid token")