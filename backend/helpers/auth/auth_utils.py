from pydantic import EmailStr
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from models import User
from schemas import UserOut, UserLoginResponse
from helpers.auth.jwt_handler import create_jwt_token, decode_jwt_token

auth_scheme = HTTPBearer()

# return user+token, else raise exception 
def generate_user_login_response(user: User) -> UserLoginResponse:
    user_out = UserOut.model_validate(user)
    token_data = create_jwt_token(user_email=user.email)
    return {"user": user_out, **token_data}


def verify_current_user(id: int, email: EmailStr, session: Session):
    user = session.get(User, id)
    if not user or user.email!=email:
        raise HTTPException(status_code=403, detail="Not allowed, access forbidden")
    return True

# get current user details from the token
def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.credentials
    decoded_token = decode_jwt_token(token)
    return decoded_token