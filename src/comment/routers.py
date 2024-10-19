from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.comment import schemas, service
from src.comment.exceptions import NonOwnerDelete, CommentNotFound

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.CreateCommentResponse
)
async def create_comment(
    new_comment: schemas.CreateComment,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.create_new_comment(current_user.id, new_comment, db)


@router.get("/all", status_code=status.HTTP_200_OK, response_model=schemas.CommentsGetAll)
async def get_all_comments(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comments = db.query(models.Comment).filter(models.Comment.user_id == current_user.id).offset(offset).limit(limit).all()
    return {"comments": comments}
