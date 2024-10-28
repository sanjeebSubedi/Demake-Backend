import os
import uuid
from datetime import datetime

from fastapi import BackgroundTasks, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import models, utils
from src.users import schemas
from src.users import utils as user_utils
from src.users.email import (
    send_account_activation_confirmation_email,
    send_account_verification_email,
)
from src.users.exceptions import (
    EmailTakenException,
    UsernameTakenException,
    UserNotFound,
)
from src.users.schemas import UserCreate


async def get_user_details(user_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise UserNotFound
    is_followed = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user_id,
            models.Follow.followed_id == user_id,
        )
        .first()
        is not None
    )
    return user, is_followed


async def create_user_account(new_user: UserCreate, db: Session, background_tasks):
    user_exists = (
        db.query(models.User).filter(models.User.email == new_user.email).first()
    )
    if user_exists:
        raise EmailTakenException
    # token = user_utils.generate_token(user.email)
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password
    new_user = models.User(**new_user.model_dump(), verified_on=None)
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError:
        raise UsernameTakenException
    db.refresh(new_user)
    await send_account_verification_email(new_user, background_tasks)
    return new_user


async def activate_user_account(token, db: Session, background_tasks: BackgroundTasks):
    decoded_email = user_utils.decode_url_safe_token(token)
    user = db.query(models.User).filter(models.User.email == decoded_email).first()
    if not user:
        raise UserNotFound
    user.verified_on = datetime.now()
    db.add(user)
    db.commit()
    db.refresh(user)
    await send_account_activation_confirmation_email(user, background_tasks)
    return user


async def update_user_details(
    username,
    full_name,
    bio,
    location,
    birth_date,
    profile_image,
    header_image,
    current_user_id,
    db: Session,
):
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user:
        raise UserNotFound
    if username is not None:
        if db.query(models.User).filter(models.User.username == username).first():
            raise UsernameTakenException
    if username:
        user.username = username
    if full_name:
        user.full_name = full_name
    if bio:
        user.bio = bio
    if location:
        user.location = location
    if birth_date:
        user.birth_date = birth_date

    if profile_image:
        profile_image_path = await save_image(profile_image, "profile-images")
        user.profile_image_url = "http://localhost:8000/" + profile_image_path

    if header_image:
        header_image_path = await save_image(header_image, "header-images")
        user.header_image_url = "http://localhost:8000/" + header_image_path
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_follow_stats(user_id, db):
    num_followers = (
        db.query(models.Follow).filter(models.Follow.followed_id == user_id).count()
    )
    num_following = (
        db.query(models.Follow).filter(models.Follow.follower_id == user_id).count()
    )
    return {"num_followers": num_followers, "num_following": num_following}


async def save_image(file: UploadFile, folder: str) -> str:
    """Save an uploaded image to the disk and return the file path."""
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format")

    upload_dir = os.path.join("static", folder)
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return os.path.join("static", folder, file_name)


async def get_user_total_tweet_count(db: Session, user_id: uuid.UUID) -> int:
    """
    Get the total number of tweets, retweets, and replies for a user
    """
    tweet_count = (
        db.query(func.count(models.Tweet.id))
        .filter(models.Tweet.user_id == user_id)
        .scalar()
    )

    retweet_count = (
        db.query(func.count(models.Retweet.id))
        .filter(models.Retweet.user_id == user_id)
        .scalar()
    )
    return tweet_count + retweet_count
