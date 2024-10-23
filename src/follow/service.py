import uuid

from sqlalchemy.orm import Session

from src import models
from src.follow import schemas
from src.follow.exceptions import (
    FollowExists,
    FollowNotExists,
    SelfFollowException,
    UserNotFound,
)


async def follow_user(user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    if user_id == current_user_id:
        raise SelfFollowException
    followed_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not followed_user:
        raise UserNotFound(status_code=404, detail="User not found")

    if (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user_id,
            models.Follow.followed_id == user_id,
        )
        .first()
    ):
        raise FollowExists

    follow_entry = models.Follow(follower_id=current_user_id, followed_id=user_id)
    db.add(follow_entry)
    db.commit()
    return {"message": f"You are now following {followed_user.username}"}


async def unfollow_user(user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    if user_id == current_user_id:
        raise SelfFollowException
    followed_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not followed_user:
        raise UserNotFound

    follow_relationship = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user_id,
            models.Follow.followed_id == user_id,
        )
        .first()
    )

    if not follow_relationship:
        raise FollowNotExists

    db.delete(follow_relationship)
    db.commit()
    return {"message": f"You have unfollowed {followed_user.username}"}


async def get_followers_details(
    user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session
):
    if not user_id:
        user_id = current_user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise UserNotFound

    followers = [follow.follower for follow in user.followers]
    followers_details = []
    for follower in followers:
        is_followed = (
            db.query(models.Follow)
            .filter(
                models.Follow.follower_id == current_user_id,
                models.Follow.followed_id == follower.id,
            )
            .first()
            is not None
        )

        followers_details.append(
            schemas.FollowUserDetails(
                full_name=follower.full_name,
                username=follower.username,
                bio=follower.bio,
                profile_image_url=follower.profile_image_url,
                is_followed=is_followed,
            )
        )
    return {"followers": followers_details}


async def get_following_details(
    user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session
):
    if not user_id:
        user_id = current_user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise UserNotFound

    following = [follow.followed for follow in user.following]
    following_details = []
    for followed in following:
        is_followed = (
            db.query(models.Follow)
            .filter(
                models.Follow.follower_id == current_user_id,
                models.Follow.followed_id == followed.id,
            )
            .first()
            is not None
        )

        following_details.append(
            schemas.FollowUserDetails(
                full_name=followed.full_name,
                username=followed.username,
                bio=followed.bio,
                profile_image_url=followed.profile_image_url,
                is_followed=is_followed,
            )
        )
    return {"following": following_details}
