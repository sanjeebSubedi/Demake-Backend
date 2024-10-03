from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import utils
from src.models import User
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
    user_exists = db.query(User).filter(User.email == new_user.email).first()
    if user_exists:
        raise EmailTakenException
    # token = user_utils.generate_token(user.email)
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password
    new_user = User(**new_user.model_dump())
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
    user = db.query(User).filter(User.email == decoded_email).first()
    if not user:
        raise UserNotFound
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    await send_account_activation_confirmation_email(user, background_tasks)
    return user
