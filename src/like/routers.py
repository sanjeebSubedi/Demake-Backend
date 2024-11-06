from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.like import schemas, service

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post(
    "", response_model=schemas.LikeResponse, status_code=status.HTTP_201_CREATED
)
async def create_like(
    like: schemas.LikeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await service.create_like(like.tweet_id, current_user.id, db)


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_like(
    tweet_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await service.delete_like(tweet_id, current_user.id, db)
