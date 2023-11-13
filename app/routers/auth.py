from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status, security
import json
from pydantic import EmailStr
from ..models import UsernameLogin, EmailLogin, ResponseLogin
from ..utils import close_connection, make_connection, verify_hash
from ..oauth_token import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["login"])

@router.post("/", response_model=ResponseLogin)
def login(credentials: security.OAuth2PasswordRequestForm = Depends()):
    db_conn, db_cursor = make_connection()
    db_cursor.execute("SELECT * FROM public.users WHERE username = %s OR email = %s;", 
                        params=(credentials.username, credentials.username))  
    user = db_cursor.fetchone()
    if not user or not verify_hash(credentials.password, user["password"]):
        close_connection(db_conn)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")
    access_token = create_access_token(data={
        "username": user["username"],
        "id": user["id"]})
    close_connection(db_conn)
    return {"access_token": access_token, "token_type": "bearer"}