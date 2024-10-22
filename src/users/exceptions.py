from fastapi import status

from src.exceptions import BadRequest, DetailedHTTPException


class EmailTakenException(BadRequest):
    DETAIL = "Email already exists."


class UsernameTakenException(BadRequest):
    DETAIL = "Username already exists."


class VerificationTokenException(BadRequest):
    DETAIL = "Verification Token Expired."    


class VerificationLinkExpired(DetailedHTTPException):
    STATUS_CODE = status.HTTP_410_GONE
    DETAIL = "Verification Link Expired"


class BadSignature(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Invalid Verification Token"


class UserNotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "User Not Found"
