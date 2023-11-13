from fastapi import APIRouter, Depends, HTTPException, status
from ..utils import close_connection, make_connection
from ..oauth_token import get_user_from_token
from ..models import BaseVote, ResponseVote

router = APIRouter(
    prefix="/votes",
    tags=["votes"]
)

@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=ResponseVote)
def send_vote(vote: BaseVote, user = Depends(get_user_from_token)):
    db_conn, db_cursor = make_connection()
    db_cursor.execute("SELECT * FROM public.votes WHERE user_id = %s AND post_id = %s;", 
                        params=(user["id"], vote.post_id))
    user_vote_post = db_cursor.fetchone()
    if user_vote_post: # There is a record, therefore, user has vote before -> Remove record (No try required because it was proven that there is a record)
        db_cursor.execute("DELETE FROM public.votes WHERE user_id = %s AND post_id = %s RETURNING *;",
                            params=(user["id"], vote.post_id))
        voting_action = "Unvoted"
    else: #There is not a record, therefore, user has not voted before -> Add record
        try:
            db_cursor.execute("INSERT INTO public.votes (user_id, post_id) VALUES (%s, %s) RETURNING *;", 
                            params=(user["id"], vote.post_id))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
        voting_action = "Voted"
    db_action = db_cursor.fetchone()
    if not db_action:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Something gone wrong.")
    db_conn.commit()
    close_connection(db_conn)
    return ResponseVote(action_type=voting_action, user_id=user["id"], post_id=vote.post_id)