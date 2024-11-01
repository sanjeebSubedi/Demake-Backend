from pathlib import Path

from fastapi.background import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.config import settings
from src.models import User
from src.users import utils as user_utils

BASE_DIR = Path(__file__).resolve().parent.parent.parent

email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_SERVER=settings.mail_server,
    MAIL_PORT=settings.mail_port,
    MAIL_FROM=settings.mail_from,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)

email_service = FastMail(email_conf)


async def send_account_verification_email(
    user: User,
    background_tasks: BackgroundTasks,
):
    token = user_utils.create_url_safe_token(user.email)
    subject = f"Account Verification - {settings.app_name}"
    activation_url = f"http://{settings.domain}/users/verify/{token}"
    data = {
        "app_name": f"{settings.app_name}",
        "name": user.username,
        "activation_url": activation_url,
    }
    message = MessageSchema(
        recipients=[user.email],
        subject=subject,
        template_body=data,
        subtype=MessageType.html,
    )
    background_tasks.add_task(
        email_service.send_message, message, template_name="user-verification.html"
    )
    return


async def send_account_activation_confirmation_email(
    user: User, background_tasks: BackgroundTasks
):
    data = {
        "app_name": settings.app_name,
        "name": user.username,
        "login_url": f"http://localhost:4200",
    }
    subject = f"Welcome - {settings.app_name}"
    message = MessageSchema(
        recipients=[user.email],
        subject=subject,
        template_body=data,
        subtype=MessageType.html,
    )
    background_tasks.add_task(
        email_service.send_message, message, template_name="verification-success.html"
    )
    return
