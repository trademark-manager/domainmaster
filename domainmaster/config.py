from pydantic import BaseSettings, Field, EmailStr, HttpUrl


class Settings(BaseSettings):
    icann_account_username: EmailStr
    icann_account_password: str
    authentication_base_url: HttpUrl = Field(default="https://account-api.icann.org")
    czds_base_url: HttpUrl = Field(default="https://czds-api.icann.org")
    working_directory: str = "."
    redis_host: str = "localhost"
    debug: bool = False
    zones_to_download: list = []
    filters: list = []

    class Config:
        allow_population_by_field_name = True
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def alias_generator(cls, string: str) -> str:
            return ".".join(string.split("_"))


class ServerSettings(BaseSettings):
    app_name: str = "TMM DomainMaster"
    host: str = "0.0.0.0"
    port: int = 5000
    log_level: str = "info"
