from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.config import settings
from src.users.exceptions import BadSignature, VerificationLinkExpired


def create_url_safe_token(email):
    serializer = URLSafeTimedSerializer(settings.secret_key)

    return serializer.dumps(email, salt=settings.security_salt)


def decode_url_safe_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(secret_key=settings.secret_key)
    try:
        token_data = serializer.loads(
            token, salt=settings.security_salt, max_age=expiration
        )
        return token_data
    except SignatureExpired:
        raise BadSignature
    except URLSafeTimedSerializer:
        raise VerificationLinkExpired
