from fastapi import status, HTTPException, APIRouter
from ..models import BaseUser, ResponseUserCreation
from ..utils import make_connection, hash_password, close_connection

router = APIRouter(
    prefix="/users",
    tags=["Users"])


@router.post("/", response_model=ResponseUserCreation, status_code=status.HTTP_201_CREATED)
def create_user(user: BaseUser):
    db_conn, db_cursor = make_connection()
    user.password = hash_password(user.password)
    try:
        db_cursor.execute(
            "INSERT INTO public.users (email, username, password) VALUES (%s, %s, %s) RETURNING *;", 
            params=(user.email, user.username, user.password))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")
    else:
        user = db_cursor.fetchone()
        return user
    finally:
        db_conn.commit()
        close_connection(db_conn)