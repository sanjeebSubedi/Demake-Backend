from typing import List

from pydantic import BaseModel, ConfigDict


class FollowUserDetails(BaseModel):
    full_name: str
    username: str
    bio: str
    profile_image_url: str | None = None
    is_followed: bool | None = False


class FollowersDetailsResponse(BaseModel):
    followers: List[FollowUserDetails]

    model_config = ConfigDict(from_attributes=True)


class FollowingDetailsResponse(BaseModel):
    following: List[FollowUserDetails]

    model_config = ConfigDict(from_attributes=True)
