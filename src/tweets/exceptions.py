from src.exceptions import (
    BadRequest,
    DetailedHTTPException,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
)


class InvaildParentTweet(BadRequest):
    DETAIL = "Parent tweet does not exist."


class TweetNotFound(NotFound):
    DETAIL = "Tweet was not found."


class NonOwnerDelete(PermissionDenied):
    DETAIL = "Unauthorized action."


class MediaUploadError(DetailedHTTPException):
    DETAIL = "Error uploading media to the server."


class EmptyTweetException(BadRequest):
    DETAIL = "Tweet must contain either text or image/video."


class TweetOverflowException(BadRequest):
    DETAIL = "Tweet content exceeds maximum length of 280 characters"


class EmptyTweetToneRequestError(BadRequest):
    DETAIL = "Cannot change the tone of an empty tweet."
