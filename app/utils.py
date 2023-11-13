from passlib.context import CryptContext
from .database import get_connection, get_cursor
from time import sleep


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_hash(plain: str, hash: str):
    return pwd_context.verify(plain, hash)

def make_connection():
    while True:
        try:
            db_conn = get_connection()
            db_cursor = get_cursor(db_conn)
            sleep(0.1)
            print("Connection opened")
            return db_conn, db_cursor
        except Exception as e:
            print(f"{e}")
            sleep(3)

def close_connection(conn):
    conn.close()
    print("Connection closed")