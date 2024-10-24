from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str
    database_username: str
    database_password: str
    database_name: str
    database_port: str
    secret_key: str
    security_salt: str
    algorithm: str
    access_token_expire_minutes: int
    domain: str

    mail_username: str
    mail_password: str
    mail_server: str
    mail_port: int
    mail_from: str
    mail_from_name: str
    mail_starttls: bool
    mail_ssl_tls: bool
    use_credentials: bool
    validate_certs: bool

    app_name: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
