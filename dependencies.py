from models.models import db, User
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_schema

def catch_session():
     try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
     finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(catch_session)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_user = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Access denied, verify the validity of your token")
    
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Invalid")
    return user
