import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.follow import schemas, service

router = APIRouter(prefix="/follow", tags=["Follow"])


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.follow_user(user_id, current_user.id, db)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return await service.unfollow_user(user_id, current_user.id, db)


@router.get(
    "/followers",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FollowersDetailsResponse,
)
async def get_followers(
    user_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await service.get_followers_details(user_id, current_user.id, db)


@router.get(
    "/following",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FollowingDetailsResponse,
)
async def get_following(
    user_id: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await service.get_following_details(user_id, current_user.id, db)
