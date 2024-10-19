from src.exceptions import BadRequest, NotAuthenticated, NotFound, PermissionDenied


class InvaildCommentId(BadRequest):
    DETAIL = "Comment Id does not exist."


class CommentNotFound(NotFound):
    DETAIL = "Comment was not found."


class NonOwnerDelete(PermissionDenied):
    DETAIL = "Unauthorized action."
