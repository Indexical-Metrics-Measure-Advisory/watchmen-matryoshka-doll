import secrets
from typing import List, Dict, Any, Optional

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = ""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    HOST_URL = "http://localhost:8000"

    ALGORITHM = "HS256"

    STORAGE_ENGINE = "mongo"

    PROJECT_NAME: str
    MONGO_HOST: str = None
    MONGO_PORT: int = None
    MONGO_USERNAME: str = None
    MONGO_PASSWORD: str = None
    PRESTO_HTTP_URL = "http://localhost:8080"
    PRESTO_HOST:str = None
    PRESTO_PORT:int = None
    PRESTO_USER = "the_user"
    PRESTO_CATALOG = "mongo"
    PRESTO_SCHEMA = "watchmen"

    MYSQL_HOST: str = ""
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = 'watchmen'
    MYSQL_POOL_MAXCONNECTIONS: int = 6
    MYSQL_POOL_MINCACHED = 2
    MYSQL_POOL_MAXCACHED = 5


    NOTIFIER_PROVIDER="email"
    EMAILS_ENABLED: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_TO:Optional[str]=None






    @validator("STORAGE_ENGINE", pre=True)
    def get_emails_enabled(cls, v: str, values: Dict[str, Any]) -> bool:
        # print(v)
        if v and v == "mongo":
            result = bool(
                values.get("MONGO_HOST")
                and values.get("MONGO_PORT"))
            if not result:
                raise ValueError("STORAGE_ENGINE dependency check MONGO_HOST and MONGO_PORT")
            else:
                return v
        elif v == "mysql":
            result = bool(
                values.get("MYSQL_HOST")
                and values.get("MYSQL_PORT")
                and values.get("MYSQL_USER")
            )
            if not result:
                raise ValueError("STORAGE_ENGINE dependency check MYSQL_HOST and MYSQL_PORT and MYSQL_USER")
            else:
                return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

    # POSTGRES_SERVER: str
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    # SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    #
    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql",
    #         user=values.get("POSTGRES_USER"),
    #         password=values.get("POSTGRES_PASSWORD"),
    #         host=values.get("POSTGRES_SERVER"),
    #         path=f"/{values.get('POSTGRES_DB') or ''}",
    #     )


    #
    # @validator("EMAILS_FROM_NAME")
    # def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
    #     if not v:
    #         return values["PROJECT_NAME"]
    #     return v
    #
    # EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    # EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    #
    #

    #
    # EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    # FIRST_SUPERUSER: EmailStr
    # FIRST_SUPERUSER_PASSWORD: str
    # USERS_OPEN_REGISTRATION: bool = False
    #


settings = Settings()
