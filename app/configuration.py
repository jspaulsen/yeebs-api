from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuration(BaseSettings):
    twitch_client_id: str
    twitch_client_secret: str
    database_url: str

    model_config = SettingsConfigDict(env_file='.env')