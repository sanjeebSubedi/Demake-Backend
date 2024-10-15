from fastapi import BackgroundTasks
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


async def create_user_account(new_user: UserCreate, db: Session, background_tasks):
    user_exists = (
        db.query(models.User).filter(models.User.email == new_user.email).first()
    )
    if user_exists:
        raise EmailTakenException
    # token = user_utils.generate_token(user.email)
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password
    new_user = models.User(**new_user.model_dump())
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
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    await send_account_activation_confirmation_email(user, background_tasks)
    return user


async def update_user_details(new_details: schemas.UserUpdate, current_user_id, db):
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user:
        raise UserNotFound
    if new_details.username is not None:
        if (
            db.query(models.User)
            .filter(models.User.username == new_details.username)
            .first()
        ):
            raise UsernameTakenException
    for key, value in new_details.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    # Commit the changes
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
