import os
from pydantic import BaseSettings, SecretStr, HttpUrl


class Settings(BaseSettings):

    DATEX_USERNAME: str
    DATEX_PASSWORD: SecretStr

    INFLUX_URL: HttpUrl
    INFLUX_BUCKET: str
    INFLUX_TOKEN: SecretStr
    INFLUX_ORG: str

    class Config:
        """Get parameter values from file."""

        env_file = os.getenv("DATEX_CONFIG_ENV", "config.env")


settings = Settings()
