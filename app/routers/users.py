from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import or_
from .. import models
from ..utils import hash_password
from sqlalchemy.orm import Session
from app.database import UsersTable, get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"])


@router.post("/", response_model=models.ResponseUserCreation, status_code=status.HTTP_201_CREATED)
def create_user(user: models.BaseUser, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    user.password = hashed_password

    existing_user = db.query(UsersTable).filter(or_(UsersTable.email == user.email, UsersTable.username == user.username)).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credentials alredy used.")

    db_user = UsersTable(**user.model_dump())

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something gone wrong. Try again in a few minutes.")
    else:
        return db_user
