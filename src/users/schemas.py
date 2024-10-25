import datetime
import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints
from sqlalchemy.orm import Session

from src import models


class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    full_name: Annotated[str, StringConstraints(max_length=100)]
    bio: Annotated[str, StringConstraints(max_length=255)] | None = None
    location: Annotated[str, StringConstraints(max_length=100)] | None = None
    birth_date: datetime.date | None = None


class UserUpdateForm(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = (
        None
    )
    full_name: (
        Annotated[str, StringConstraints(min_length=1, max_length=100)] | None
    ) = None
    bio: Annotated[str, StringConstraints(max_length=255)] | None = None
    location: Annotated[str, StringConstraints(max_length=100)] | None = None
    birth_date: datetime.date | None = None


class CreateUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    full_name: str
    bio: str | None = None
    location: str | None = None
    birth_date: datetime.date | None = None
    created_at: datetime.datetime
    verified_on: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateUserResponse(BaseModel):
    username: str
    full_name: str
    bio: str | None = None
    location: str | None = None
    birth_date: datetime.date | None = None
    profile_image_url: str | None = None
    header_image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserDetailsBase(BaseModel):
    id: uuid.UUID
    full_name: str
    username: str
    bio: str | None = None
    location: str | None = None
    profile_image_url: str | None = None
    header_image_url: str | None = None
    verified_on: datetime.datetime
    num_followers: int | None = -1
    num_following: int | None = -1
    tweet_count: int | None = -1


class UserDetailsResponse(UserDetailsBase):
    is_followed: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class CurrentUserDetailsResponse(UserDetailsBase):
    birth_date: datetime.date | None = None

    model_config = ConfigDict(from_attributes=True)
