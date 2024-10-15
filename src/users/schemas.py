import datetime
import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    # full_name: Annotated[str, StringConstraints(max_length=100)]
    bio: Annotated[str, StringConstraints(max_length=255)] | None = None
    location: Annotated[str, StringConstraints(max_length=100)] | None = None
    birth_date: datetime.date | None = None


class UserUpdate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = (
        None
    )
    bio: Annotated[str, StringConstraints(max_length=255)] | None = None
    location: Annotated[str, StringConstraints(max_length=100)] | None = None
    birth_date: datetime.date | None = None


class CreateUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    # full_name: str
    bio: str | None = None
    location: str | None = None
    birth_date: datetime.date | None = None
    created_at: datetime.datetime
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
