from fastapi import Depends
from sqlalchemy.orm import Session

from src import models
from src.auth.jwt import oauth2_scheme, verify_access_token
from src.database import get_db


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    token = verify_access_token(token)
    user_obj = db.query(models.User).filter(models.User.email == token.id).first()
    return user_obj
