from src.exceptions import BadRequest, NotFound


class AlreadyLiked(BadRequest):
    DETAIL = "Tweet has already been liked."


class TweetNotFound(NotFound):
    DETAIL = "Tweet was not found."


class LikeNotFound(NotFound):
    DETAIL = "Like does not exist."
