import random
import uuid

from sqlalchemy import and_, not_, select
from sqlalchemy.orm import Session

from src import models
from src.follow import schemas
from src.follow.exceptions import (
    FollowExists,
    FollowNotExists,
    SelfFollowException,
    UserNotFound,
)
from src.logger import get_logger

logger = get_logger()


async def follow_user(user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    if user_id == current_user_id:
        logger.warning(
            f"Follow failed: User {current_user_id} attempted to follow themselves"
        )
        raise SelfFollowException
    followed_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not followed_user:
        logger.warning(f"Follow failed: Target user {user_id} not found")
        raise UserNotFound(status_code=404, detail="User not found")

    if (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user_id,
            models.Follow.followed_id == user_id,
        )
        .first()
    ):
        logger.warning(
            f"Follow failed: User {current_user_id} already follows {user_id}"
        )
        raise FollowExists

    follow_entry = models.Follow(follower_id=current_user_id, followed_id=user_id)
    db.add(follow_entry)
    db.commit()
    logger.info(f"User {current_user_id} successfully followed user {user_id}")
    return {"message": f"You are now following {followed_user.username}"}


async def unfollow_user(user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    if user_id == current_user_id:
        logger.warning(
            f"Unfollow failed: User {current_user_id} attempted to unfollow themselves"
        )
        raise SelfFollowException
    followed_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not followed_user:
        logger.warning(f"Unfollow failed: Target user {user_id} not found")
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
        logger.warning(
            f"Unfollow failed: User {current_user_id} doesn't follow {user_id}"
        )
        raise FollowNotExists

    db.delete(follow_relationship)
    db.commit()
    logger.info(f"User {current_user_id} successfully unfollowed user {user_id}")
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
                id=follower.id,
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


async def get_follow_suggestions(
    current_user_id: uuid.UUID, db: Session, limit: int = 5
):
    following_subquery = select(models.Follow.followed_id).where(
        models.Follow.follower_id == current_user_id
    )

    query = select(
        models.User.id,
        models.User.full_name,
        models.User.username,
        models.User.profile_image_url,
    ).where(
        and_(
            models.User.id != current_user_id,
            not_(models.User.id.in_(following_subquery)),
        )
    )

    result = db.execute(query)
    users = result.all()

    suggested_users = random.sample(users, min(len(users), limit))

    return [
        dict(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            profile_image_url=user.profile_image_url,
        )
        for user in suggested_users
    ]
