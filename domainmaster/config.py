from pydantic import BaseSettings, BaseModel, Field


class Settings(BaseModel):
    icann_account_username: str = Field(alias="icann.account.username")
    icann_account_password: str = Field(alias="icann.account.password")
    authentication_base_url: str = Field(alias="authentication.base.url", default="https://account-api.icann.org")
    czds_base_url: str = Field(alias="czds.base.url", default="https://czds-api.icann.org")
    working_directory: str = Field(alias="working.directory", default=".")
    debug: bool = False
    zones_to_download: list = []
    filters: list = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ServerSettings(BaseSettings):
    app_name: str = "TMM DomainMaster"
    host: str = "0.0.0.0"
    port: int = 5000
    log_level: str = "info"
