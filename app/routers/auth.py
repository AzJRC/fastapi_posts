from fastapi import APIRouter, Depends, HTTPException, status, security
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db, UsersTable
from ..models import ResponseLogin
from ..utils import verify_hash
from ..oauth_token import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["login"])

@router.post("/", response_model=ResponseLogin)
def login(credentials: security.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute("SELECT * FROM public.users WHERE username = %s OR email = %s;", 
    #                     params=(credentials.username, credentials.username))  
    # user = db_cursor.fetchone()
    user = db.query(UsersTable).filter(or_(UsersTable.email == credentials.username, UsersTable.username == credentials.username)).first()
    print(user)
    if not user or not verify_hash(credentials.password, user.password):
        #close_connection(db_conn)
        db.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")
    access_token = create_access_token(data={
        "username": user.username,
        "id": user.id})
    #close_connection(db_conn)
    db.close()
    return {"access_token": access_token, "token_type": "bearer"}