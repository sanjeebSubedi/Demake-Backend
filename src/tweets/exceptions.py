from src.exceptions import BadRequest, NotAuthenticated, NotFound, PermissionDenied


class InvaildParentTweet(BadRequest):
    DETAIL = "Parent tweet does not exist."


class TweetNotFound(NotFound):
    DETAIL = "Tweet was not found."


class NonOwnerDelete(PermissionDenied):
    DETAIL = "Unauthorized action."
