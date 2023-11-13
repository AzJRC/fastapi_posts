from typing import Any, List, Union
from fastapi import Depends, status, HTTPException, APIRouter
from ..models import BasePost, ResponsePost, DataToken
from ..utils import make_connection, close_connection
from ..oauth_token import get_user_from_token

router = APIRouter(
    prefix="/posts",
    tags=["Posts"])

INTEGER_LIMIT = 9223372036854775807
QUERY_GET_USER_BY_ID = """
    SELECT
        users.id,
        users.email,
        users.username,
        COUNT(votes.user_id) AS votes_given
    FROM votes
    LEFT JOIN users ON votes.user_id = users.id
    WHERE users.id = %s
    GROUP BY 
        votes.user_id, 
        users.id, 
        users.email, 
        users.username"""

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

QUERY_UPDATE_POST_WITH_VOTE_COUNT = """
    UPDATE public.posts 
        SET title = %s, content = %s, published = %s, last_update = NOW()
        FROM (
            SELECT post_id, COUNT(user_id) AS post_votes
            FROM votes
            WHERE post_id = %s
            GROUP BY post_id
        ) AS vote_counts
        WHERE public.posts.id = vote_counts.post_id
        AND public.posts.id = %s
        RETURNING *"""

@router.get("/", response_model=List[ResponsePost])
def read_posts(user=Depends(get_user_from_token), limit: int = INTEGER_LIMIT, offset: int = 0):
    db_conn, db_cursor = make_connection()
    db_cursor.execute(
        f"{QUERY_POSTS_WITH_VOTE_COUNT} LIMIT %s OFFSET %s;", params=(limit, offset))
    post_query = db_cursor.fetchall()
    for post in post_query:
        db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post["user_id"],))
        user_query = db_cursor.fetchone()
        post["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    close_connection(db_conn)
    return post_query


@router.get("/{id}", response_model=ResponsePost)
def read_post(id: int, user=Depends(get_user_from_token)):
    db_conn, db_cursor = make_connection()
    db_cursor.execute(f"{QUERY_POSTS_WITH_VOTE_COUNT} WHERE id = %s",
                      params=(str(id),))
    post_query = db_cursor.fetchone()
    if not post_query:
        close_connection(db_conn)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post_query["user_id"],))
    user_query = db_cursor.fetchone()
    post_query["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    close_connection(db_conn)
    return post_query


@router.post("/", response_model=ResponsePost, status_code=status.HTTP_201_CREATED)
def create_post(post: BasePost, user: DataToken = Depends(get_user_from_token)):
    db_conn, db_cursor = make_connection()
    try:
        db_cursor.execute("INSERT INTO public.posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING *;",
                        params=(post.title, post.content, post.published, user["id"]))
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect post.")
    post_query = db_cursor.fetchone()
    db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post_query["user_id"],))  # Include user details in the post
    user_query = db_cursor.fetchone()
    post_query["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    db_conn.commit()
    close_connection(db_conn)
    return post_query


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, user: DataToken = Depends(get_user_from_token)):
    db_conn, db_cursor = make_connection()
    db_cursor.execute("DELETE FROM public.posts WHERE id = %s;",
                      params=(str(id),))
    post_query = db_cursor.fetchone()
    if not post_query:
        close_connection(db_conn)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found.")
    if user["id"] != post_query["user_id"]:
        close_connection(db_conn)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to do this action.")
    db_conn.commit()
    close_connection(db_conn)
    return


@router.put("/{id}", response_model=ResponsePost, status_code=status.HTTP_205_RESET_CONTENT)
def update_post(post: BasePost, id: int, user: DataToken = Depends(get_user_from_token)):
    db_conn, db_cursor = make_connection()
    db_cursor.execute(f"{QUERY_UPDATE_POST_WITH_VOTE_COUNT};", params=(post.title, post.content, post.published, str(id), str(id)))
    post_query = db_cursor.fetchone()
    if not post_query:
        close_connection(db_conn)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    if user["id"] != post_query["user_id"]:
        close_connection(db_conn)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to do this action.")
    db_cursor.execute(f"{QUERY_GET_USER_BY_ID};", params=(post_query["user_id"],))
    user_query = db_cursor.fetchone()
    post_query["user"] = user_query #Add user info to post_query to comply with the ResponsePost model
    db_conn.commit()
    close_connection(db_conn)
    print(post_query)
    return post_query
