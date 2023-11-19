from typing import Any, List, Union
from fastapi import Depends, status, HTTPException, APIRouter
from app.database import UsersTable, get_db
from ..models import BasePost, ResponsePost, DataToken
from ..utils import make_connection, close_connection
from ..oauth_token import get_user_from_token
from sqlalchemy import insert, delete, update
from sqlalchemy.orm import Session
from app.database import PostsTable

router = APIRouter(
    prefix="/posts",
    tags=["Posts"])

INTEGER_LIMIT = 9223372036854775807

QUERY_GET_USER_BY_ID = """
    SELECT
        users.email,
        users.username,
        COUNT(votes.user_id) AS votes_given
    FROM users
    LEFT JOIN votes ON users.id = votes.user_id
    WHERE id = %s
    GROUP BY 
        votes.user_id, 
        users.id, 
        users.email, 
        users.username;"""

QUERY_POSTS_WITH_VOTE_COUNT = """
    SELECT
        posts.id,
        posts.title,
        posts.content,
        posts.published,
        posts.creation_date,
        posts.last_update,
        posts.user_id,
        COUNT(votes.user_id) AS post_votes
    FROM public.posts
    LEFT JOIN votes ON posts.id = votes.post_id
    GROUP BY
        posts.id,
        posts.title,
        posts.content,
        posts.published,
        posts.creation_date,
        posts.last_update,
        posts.user_id"""

QUERY_POST_WITH_VOTE_COUNT = """
    SELECT
        posts.id,
        posts.title,
        posts.content,
        posts.published,
        posts.creation_date,
        posts.last_update,
        posts.user_id,
        COUNT(votes.user_id) AS post_votes
    FROM public.posts
    LEFT JOIN votes ON posts.id = votes.post_id
    WHERE id = %s
    GROUP BY
        posts.id,
        posts.title,
        posts.content,
        posts.published,
        posts.creation_date,
        posts.last_update,
        posts.user_id"""

QUERY_UPDATE_POST_WITH_VOTE_COUNT = """
    UPDATE public.posts 
        SET title = %s, content = %s, published = %s, last_update = NOW()
        WHERE public.posts.id = %s"""

@router.get("/", response_model=List[ResponsePost])
def read_posts(user=Depends(get_user_from_token), db: Session = Depends(get_db), limit: int = INTEGER_LIMIT, offset: int = 0):
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute(
    #     f"{QUERY_POSTS_WITH_VOTE_COUNT} LIMIT %s OFFSET %s;", params=(limit, offset))
    # post_query = db_cursor.fetchall()
    # for post in post_query:
    #     db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post["user_id"],))
    #     user_query = db_cursor.fetchone()
    #     post["user"] = user_query
    #close_connection(db_conn)

    try:
        post_query = db.query(PostsTable).join(UsersTable, PostsTable.user_id == UsersTable.id).limit(limit).offset(offset).all()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return post_query


@router.get("/{id}", response_model=ResponsePost)
def read_post(id: int, user=Depends(get_user_from_token), db: Session = Depends(get_db)):
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute(f"{QUERY_POST_WITH_VOTE_COUNT};",
    #                   params=(str(id),))
    # post_query = db_cursor.fetchone()
    # if not post_query:
    #     close_connection(db_conn)
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    # db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post_query["user_id"],))
    # user_query = db_cursor.fetchone()
    # post_query["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    # close_connection(db_conn)
    # print(post_query)

    try:
        post_query = db.query(PostsTable).join(UsersTable, PostsTable.user_id == UsersTable.id).filter(PostsTable.id == id).first()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post_query


@router.post("/", response_model=ResponsePost, status_code=status.HTTP_201_CREATED)
def create_post(post: BasePost, user: DataToken = Depends(get_user_from_token), db: Session = Depends(get_db)):
    # db_conn, db_cursor = make_connection()
    # try:
    #     db_cursor.execute("INSERT INTO public.posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING *;",
    #                     params=(post.title, post.content, post.published, user["id"]))
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect post.")
    # post_query = db_cursor.fetchone()
    # db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post_query["user_id"],))  # Include user details in the post
    # user_query = db_cursor.fetchone()
    # post_query["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    # print(post_query)
    # db_conn.commit()
    # close_connection(db_conn)

    post_query = PostsTable(**post.model_dump())
    post_query.user_id = user.id
    try:
        db.add(post_query)
        db.commit()
        db.refresh(post_query)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return post_query


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, user: DataToken = Depends(get_user_from_token), db: Session = Depends(get_db)):
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute("DELETE FROM public.posts WHERE id = %s RETURNING *;",
    #                   params=(str(id),))
    # post_query = db_cursor.fetchone()
    # if not post_query:
    #     close_connection(db_conn)
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="Post not found.")
    # if user["id"] != post_query["user_id"]:
    #     close_connection(db_conn)
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You are not allowed to do this action.")
    # db_conn.commit()
    # close_connection(db_conn)
    
    existing_post = db.query(PostsTable).filter(PostsTable.id == id).first()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    try:
        db.delete(existing_post)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    db.commit()
    return


@router.put("/{id}", response_model=ResponsePost, status_code=status.HTTP_205_RESET_CONTENT)
def update_post(post: BasePost, id: int, user: DataToken = Depends(get_user_from_token), db: Session = Depends(get_db)):
    # db_conn, db_cursor = make_connection()
    # db_cursor.execute(f"{QUERY_UPDATE_POST_WITH_VOTE_COUNT} RETURNING *;", params=(post.title, post.content, post.published, str(id)))
    # post_query = db_cursor.fetchone()
    # if not post_query:
    #     close_connection(db_conn)
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    # if user["id"] != post_query["user_id"]:
    #     close_connection(db_conn)
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You are not allowed to do this action.")
    # db_conn.commit()
    # close_connection(db_conn)

    existing_post = db.query(PostsTable).filter(PostsTable.id == id).first()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    try:
        existing_post.title = post.title
        existing_post.content = post.content
        existing_post.published = post.published
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    db.commit()
    return existing_post

