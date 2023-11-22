from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime

from app.database import PostsTable

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


class UserDetailsModel(BaseModel):
    email: EmailStr
    username: str


class ResponsePost(BaseModel):
    title: str
    content: str
    published: bool
    creation_date: datetime.datetime
    last_update: datetime.datetime
    post_id: int 
    user_id: int
    user_details: UserDetailsModel
    post_votes: int = 0

class ResponsePost_forCUD(BaseModel):
    title: str
    content: str
    published: bool
    creation_date: datetime.datetime
    last_update: datetime.datetime
    post_id: int

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
