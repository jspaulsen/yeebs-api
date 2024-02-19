from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuration(BaseSettings):
    twitch_client_id: str
    twitch_client_secret: str
    database_url: str
    log_level: str = "INFO"
    redirect_host: str = "http://localhost:3000"

    twitch_scope: list[str] = ['bits:read', 'channel:read:redemptions', 'channel:read:ads']
    frontend_url: str = 'https://www.yeebs.dev'

    model_config = SettingsConfigDict(env_file='.env')