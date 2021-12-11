from typing import List, Dict, Any, Optional

from pydantic import AnyHttpUrl, BaseSettings, validator

DEV = "dev"
PROD = "production"


class Settings(BaseSettings):
    API_V1_STR: str = ""
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = '801GtEAdlE8o-iZRLBMgz30PGE_zxry82EaUYMAhNq8'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    DASK_ON: bool = False
    DASK_PROCESSES: bool = False
    DASK_TEMP: str = None

    ENVIRONMENT: str = DEV

    ALGORITHM = "HS256"
    STORAGE_ENGINE = "mongo"
    PROJECT_NAME: str
    MONGO_HOST: str = None
    MONGO_PORT: int = None
    MONGO_DATABASE: str = "watchmen"
    MONGO_USERNAME: str = None
    MONGO_PASSWORD: str = None
    PRESTO_HOST: str = None
    PRESTO_PORT: int = None
    PRESTO_USER = "the_user"
    PRESTO_CATALOG = "mongo"
    PRESTO_SCHEMA = "watchmen"
    PRESTO_ON = True
    PRESTO_LIB = "trino"

    DEFAULT_DATA_ZONE_ON = False

    MYSQL_HOST: str = ""
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "watchmen"
    MYSQL_POOL_MAXCONNECTIONS: int = 6
    MYSQL_POOL_MINCACHED = 2
    MYSQL_POOL_MAXCACHED = 5
    MYSQL_ECHO = False

    ORACLE_LIB_DIR: str = ""
    ORACLE_HOST: str = ""
    ORACLE_PORT: int = 1521
    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""
    ORACLE_SERVICE: str = ""
    ORACLE_SID: str = ""
    ORACLE_NAME: str = ""

    CONNECTOR_KAFKA = False
    CONNECTOR_RABBITMQ = False

    RABBITMQ_HOST: str = ""
    RABBITMQ_PORT: str = "5672"
    RABBITMQ_USERNAME: str = ""
    RABBITMQ_PASSWORD: str = ""
    RABBITMQ_VIRTUALHOST: str = ""
    RABBITMQ_QUEUE: str = ""
    RABBITMQ_DURABLE: bool = True
    RABBITMQ_AUTO_DELETE: bool = False

    KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
    KAFKA_TOPICS = ""

    NOTIFIER_PROVIDER = "email"
    EMAILS_ENABLED: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_TO: Optional[str] = None
    TOPIC_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    DECIMAL = "decimal(32,2)"

    MOCK_USER = "demo_user"
    SNOWFLAKE_DATACENTER = 0
    SNOWFLAKE_WORKER = 0
    SNOWFLAKE_REMOTE = False
    SNOWFLAKE_REMOTE_HOST: str = None

    MULTIPLE_DATA_SOURCE = False
    EXTERNAL_WRITER_ON = True

    PROMETHEUS_ON = False

    INDEX_ON = False

    PIPELINE_MONITOR_ON = True

    QUERY_MONITOR_ON = False

    KEY_MANAGEMENT_TYPE: str = "db"  ## 'aws-kms' 'azure-kms' , 'aliyun-kms'

    DATA_SECURITY_ON = False

    @validator("STORAGE_ENGINE", pre=True)
    def check_storage_configuration(cls, v: str, values: Dict[str, Any]) -> bool:
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
        elif v == "oracle":
            result = bool(
                values.get("ORACLE_HOST")
                and values.get("ORACLE_PORT")
                and values.get("ORACLE_USER")
                and values.get("ORACLE_LIB_DIR")
                and values.get("ORACLE_SERVICE")
            )
            if not result:
                raise ValueError("STORAGE_ENGINE dependency check ORACLE_HOST and ORACLE_PORT and ORACLE_USER")
            else:
                return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
