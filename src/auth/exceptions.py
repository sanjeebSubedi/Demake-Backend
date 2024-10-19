from src.exceptions import BadRequest, NotAuthenticated, NotFound, PermissionDenied


class InvalidCredentials(NotAuthenticated):
    DETAIL = "Invalid credentials."


class InvalidToken(NotAuthenticated):
    DETAIL = "Invalid refresh token."


class AuthorizationFailed(PermissionDenied):
    DETAIL = "Authorization failed."
