import logging
import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    LOCAL = "local"


def to_bool(s: str) -> bool:
    return s.lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
        "yeah",
        "yup",
        "certainly",
        "uh-huh",
    ]


class GlobalConfig(BaseSettings):
    TITLE: str = os.environ.get("ENDORSER_PUBLIC_NAME", "Endorser")
    DESCRIPTION: str = (
        os.environ.get("ENDORSER_PUBLIC_DESC", "An endorser service for aca-py wallets")
    )

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False
    TESTING: bool = False
    TIMEZONE: str = "UTC"

    # configuration
    ENDORSER_AUTO_ACCEPT_CONNECTIONS: bool = to_bool(
        os.environ.get("ENDORSER_AUTO_ACCEPT_CONNECTIONS", "false")
    )
    ENDORSER_AUTO_ACCEPT_AUTHORS: bool = to_bool(
        os.environ.get("ENDORSER_AUTO_ACCEPT_AUTHORS", "false")
    )
    ENDORSER_AUTO_ENDORSE_REQUESTS: bool = to_bool(
        os.environ.get("ENDORSER_AUTO_ENDORSE_REQUESTS", "false")
    )
    ENDORSER_AUTO_ENDORSE_TXN_TYPES: str = os.environ.get(
        "ENDORSER_AUTO_ENDORSE_TXN_TYPES", ""
    )

    ENDORSER_REJECT_BY_DEFAULT: bool = to_bool(
        os.environ.get("ENDORSER_REJECT_BY_DEFAULT", "false")
    )

    # the following defaults match up with default values in scripts/.env.example
    # these MUST be all set in non-local environments.
    PSQL_HOST: str = os.environ.get("CONTROLLER_POSTGRESQL_HOST", "localhost")
    PSQL_PORT: int = os.environ.get("CONTROLLER__POSTGRESQL_PORT", 5432)
    PSQL_DB: str = os.environ.get("CONTROLLER_POSTGRESQL_DB", "endorser_controller_db")

    PSQL_USER: str = os.environ.get("CONTROLLER_POSTGRESQL_USER", "")
    PSQL_PASS: str = os.environ.get("CONTROLLER_POSTGRESQL_PASSWORD", "")

    PSQL_ADMIN_USER: str = os.environ.get(
        "CONTROLLER_POSTGRESQL_ADMIN_USER", ""
    )
    PSQL_ADMIN_PASS: str = os.environ.get(
        "CONTROLLER_POSTGRESQL_ADMIN_PASSWORD", ""
    )

    # application connection is async
    # fmt: off
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"  # noqa: E501
    )
    # migrations connection uses owner role and is synchronous
    SQLALCHEMY_DATABASE_ADMIN_URI: str = (
        f"postgresql://{PSQL_ADMIN_USER}:{PSQL_ADMIN_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"  # noqa: E501
    )
    # fmt: on

    ACAPY_ADMIN_URL: str = os.environ.get("ACAPY_ADMIN_URL", "http://localhost:9031")
    ACAPY_ADMIN_URL_API_KEY: str = os.environ.get("ACAPY_API_ADMIN_KEY", "change-me")
    ACAPY_WALLET_AUTH_TOKEN: str | None = os.environ.get("ACAPY_WALLET_AUTH_TOKEN")

    ENDORSER_API_ADMIN_USER: str = os.environ.get("ENDORSER_API_ADMIN_USER", "endorser")
    ENDORSER_API_ADMIN_KEY: str = os.environ.get("ENDORSER_API_ADMIN_KEY", "change-me")

    ENDORSER_WEBHOOK_URL: str = os.environ.get(
        "ENDORSER_WEBHOOK_URL", "http://aries-endorser-api:5000/webhook"
    )
    ACAPY_WEBHOOK_URL_API_KEY_NAME: str = "x-api-key"
    ACAPY_WEBHOOK_URL_API_KEY: str = os.environ.get("ACAPY_WEBHOOK_URL_API_KEY", "")

    DB_ECHO_LOG: bool = False

    # Api V1 prefix
    API_V1_STR: str = "/v1"

    # openssl rand -hex 32
    JWT_SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    model_config = SettingsConfigDict(case_sensitive=True)


class LocalConfig(GlobalConfig):
    """Local configurations."""

    DEBUG: bool = True
    DB_ECHO_LOG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.LOCAL


class ProdConfig(GlobalConfig):
    """Production configurations."""

    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.PRODUCTION


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalConfig:
        if self.environment == EnvironmentEnum.LOCAL.value:
            return LocalConfig()
        return ProdConfig()


@lru_cache()
def get_configuration() -> GlobalConfig:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()
