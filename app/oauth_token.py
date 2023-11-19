from . import models
from .settings import settings
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, security, status
from app.database import UsersTable, get_db
from sqlalchemy.orm import Session
#from .utils import close_connection, make_connection

# From env vars
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

OAUTH_SCHEME = security.OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_username = payload.get("username")
        user_id = payload.get("id")
        expiration = payload.get("exp")
        if not user_username or not user_id or datetime.utcnow() > datetime.utcfromtimestamp(expiration):
            raise credential_exception
        token_data = models.DataToken(id=user_id, username=user_username)
    except JWTError as e:
        print(e)
        raise credential_exception
    return token_data
    
def get_user_from_token(token: str = Depends(OAUTH_SCHEME), db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                         detail="Could not validate credentials.", 
                                         headers={"WWW-Authenticate": "Bearer"})
    user_auth = verify_token(token, credential_exception)
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute("SELECT * FROM public.users WHERE id = %s AND username = %s", params=(user_auth.id,user_auth.username))
    # user = db_cursor.fetchone()
    #close_connection(db_conn)
    user = db.query(UsersTable).filter(UsersTable.id == user_auth.id, UsersTable.username == user_auth.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist.")
    return user