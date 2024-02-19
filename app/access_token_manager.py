import logging

from pydantic import BaseModel
import pendulum

from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.models.oauth_token import OAuthToken
from app.models.sql.authorization_token import AuthorizationToken, Origin


logger = logging.getLogger(__name__)


class AccessToken(BaseModel):
    access_token: str
    expires_at: pendulum.DateTime

    class Config:
        arbitrary_types_allowed: bool = True


class AccessTokenManager:
    def __init__(self, configuration: Configuration) -> None:
        self.access_tokens: dict[str, AccessToken] = {}
        self.client_mapping = {
            Origin.Twitch: TwitchClient(
                configuration.twitch_client_id,
                configuration.twitch_client_secret,
            ),
        }
    
    def _add(self, service: str, sub_id: str, access_token: AccessToken) -> None:
        self.access_tokens[f"{service}_{sub_id}"] = access_token

    def add_access_token(self, service: str, sub_id: str, oauth_token: OAuthToken) -> None:
        self._add(
            service,
            sub_id,
            AccessToken(
                access_token=oauth_token.access_token,
                expires_at=pendulum.now().add(seconds=oauth_token.expires_in - 15),
            ),
        )

    async def get_access_token(self, service: str, sub_id: str) -> str | None:
        access_token = self.access_tokens.get(f"{service}_{sub_id}")

        if not access_token or access_token.expires_at < pendulum.now():
            client = self.client_mapping.get(service)

            if not client:
                return None
            
            auth_token = await AuthorizationToken.get_or_none(sub_id=sub_id, origin=service)

            if not auth_token:
                return None
            
            try:
                token = await client.refresh_token(auth_token.refresh_token)
            except Exception as e:
                logger.exception(
                    f"An error occurred while refreshing a token: {e}",
                    extra={
                        "error": e,
                    },
                )

                return None
            
            auth_token.refresh_token = token.refresh_token
            await auth_token.save()

            access_token = AccessToken(
                access_token=token.access_token,
                expires_at=pendulum.now().add(seconds=token.expires_in - 15),
            )

            self._add(service, sub_id, access_token)
        
        return access_token.access_token