import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.retweet import schemas, service

router = APIRouter(prefix="/retweets", tags=["Retweets"])


@router.post(
    "",
    response_model=schemas.RetweetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_retweet(
    retweet: schemas.RetweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await service.create_retweet(
        tweet_id=retweet.tweet_id, current_user_id=current_user.id, db=db
    )


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_retweet(
    tweet_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await service.delete_retweet(
        tweet_id=tweet_id, current_user_id=current_user.id, db=db
    )
