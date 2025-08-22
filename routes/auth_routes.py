from fastapi import APIRouter, Depends, HTTPException
from models.models import User
from dependencies import catch_session, verify_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas.auth_schema import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(id_user, duration_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + duration_token
    dic_info = {"sub": str(id_user), "exp": expiration_date}
    encoded_jwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    
    return encoded_jwt

def authenticate_user(email, password, session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user
    


@auth_router.get("/")
async def home():
    return {"message": "You accessed the authentication endpoint", "authenticated": False}

@auth_router.post("/register")
async def register_user(user_schema: UserSchema, session: Session = Depends(catch_session,)):
    user = session.query(User).filter(User.email == user_schema.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    else:
        encrypted_password = bcrypt_context.hash(user_schema.password)
        new_user = User(user_schema.name, user_schema.email, encrypted_password, user_schema.active, user_schema.admin)
        session.add(new_user)
        session.commit()
        return {"message": f"User {user_schema.name} registred successfully"}   
    
@auth_router.post("/login")
async def login_user(login_schema: LoginSchema, session: Session = Depends(catch_session)):
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:  
        raise HTTPException(status_code=400, detail="User not found or invalid credentials")
    else:
       access_token = create_token(user.id)
       refresh_token = create_token(user.id, duration_token=timedelta(days=7))
       return {
           "access_token": access_token,
           "refresh_token": refresh_token,
           "token_type": "Bearer",
       }
    
@auth_router.post("/login-form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(catch_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:  
        raise HTTPException(status_code=400, detail="User not found or invalid credentials")
    else:
       access_token = create_token(user.id)
       return {
           "access_token": access_token,
           "token_type": "Bearer",
       }

    
@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
           "access_token": access_token,
           "token_type": "Bearer",
       }
