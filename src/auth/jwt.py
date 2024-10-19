import datetime
from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src import models
from src.auth import schemas
from src.auth.exceptions import InvalidCredentials, InvalidToken
from src.config import settings
from src.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        id: str = payload.get("user_id")
        if not id:
            raise InvalidToken

        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise InvalidCredentials
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    token = verify_access_token(token)
    user_obj = db.query(models.User).filter(models.User.user_id == token.id).first()
    return user_obj
