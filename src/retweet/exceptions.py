from src.exceptions import BadRequest, NotFound


class TweetNotFound(NotFound):
    DETAIL = "Tweet was not found."


class AlreadyRetweeted(BadRequest):
    DETAIL = "Tweet has already been retweeted."


class RetweetNotFound(NotFound):
    DETAIL = "Retweet does not exist."
