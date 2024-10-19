from datetime import datetime
import uuid
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


class CreateComment(BaseModel):
    comment_text: Annotated[str, StringConstraints(min_length=1, max_length=500)]

class CreateCommentResponse(BaseModel):
    id: uuid.UUID
    comment_text: str
    parent_comment_id: uuid.UUID
    time_stamp: datetime 
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class CommentGet(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    comment_text: str
    time_stamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CommentsGetAll(BaseModel):
    tweets: List[CommentGet]

    model_config = ConfigDict(from_attributes=True)
