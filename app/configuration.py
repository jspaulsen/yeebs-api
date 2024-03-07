from typing import Any, Type
from pydantic import GetCoreSchemaHandler, ValidationInfo
from pydantic_core import core_schema
from pydantic_settings import BaseSettings, SettingsConfigDict


class ByteString(bytes):
    @staticmethod
    def fromhex(input: Any, _info: ValidationInfo) -> bytes:
        return bytes.fromhex(input)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        _: Type[Any], 
        __: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(cls.fromhex)
    

class Configuration(BaseSettings):
    twitch_client_id: str
    twitch_client_secret: str
    spotify_client_id: str
    spotify_client_secret: str
    database_url: str
    log_level: str = "INFO"
    redirect_host: str = "https://api.yeebs.dev" # "http://localhost:3000"

    twitch_scope: list[str] = ['bits:read', 'channel:read:redemptions', 'channel:read:ads', 'user:read:chat', 'user:bot']
    spotify_scope: list[str] = [ 'user-modify-playback-state', 'user-read-playback-state' ]
    twitch_subscription_secret: str
    
    frontend_url: str = "https://api.yeebs.dev/userinfo" # 'http://localhost:3000/userinfo'

    model_config = SettingsConfigDict(env_file='.env')
    aes_encryption_key: ByteString
    jwt_secret_key: bytes
    
    is_local: bool = False
    jwt_expiration: int = 3600
