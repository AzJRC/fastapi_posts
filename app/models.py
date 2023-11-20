from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime

# User models

class ResponseUserCreation(BaseModel):
    email: EmailStr
    username: str

class ResponseUser(BaseModel):
    email: EmailStr
    username: str

class BaseUser(ResponseUser):
    password: str

class ResponseUserWithVotes(ResponseUser):
    votes_given: Optional[int] = 0

# Post Models

class BasePost(BaseModel):
    title: str
    content: str
    published: bool = True
    
class ExtraPost(BasePost):
    creation_date: datetime.datetime
    last_update: datetime.datetime
    user_id: int
    user: ResponseUser
class ResponsePost(BaseModel):
    PostsTable: ExtraPost
    vote_count: int

# Login models

class EmailLogin(BaseModel):
    email: EmailStr
    password: str

class UsernameLogin(BaseModel):
    username: str
    password: str

class ResponseLogin(BaseModel): 
    access_token: str
    token_type: str

# Token models

class Token(BaseModel):
    access_token: str
    token_type: str

class DataToken(BaseModel):
    id: int 
    username: str

# Vote models

class BaseVote(BaseModel):
    post_id: int

class ResponseVote(BaseModel):
    message: str = "Action successful"
    action_type: str 
    user_id: int
    post_id: int