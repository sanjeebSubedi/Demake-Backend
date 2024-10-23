from fastapi import status

from src.exceptions import BadRequest, DetailedHTTPException


class UserNotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "User Not Found"


class FollowExists(BadRequest):
    DETAIL = "User is already followed"


class FollowNotExists(BadRequest):
    DETAIL = "User is not followed"


class SelfFollowException(BadRequest):
    DETAIL = "Cannot follow/unfollow yourself"
