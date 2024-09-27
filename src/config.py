from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str
    database_username: str
    database_password: str
    database_name: str
    database_port: str
    secret_key: str
    security_password_salt: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
