import logging
import httpx

from pydantic import BaseModel
import pendulum
from tortoise.transactions import in_transaction

from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.models.encrypted import Encrypted
from app.models.oauth_token import OAuthToken
from app.models.sql.authorization_token import AuthorizationToken, Origin


REDUCED_EXPIRATION = 60


logger = logging.getLogger(__name__)


class AccessToken(BaseModel):
    access_token: str
    expires_at: pendulum.DateTime

    class Config:
        arbitrary_types_allowed: bool = True


class Authorization:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.client_mapping = {
            Origin.Twitch: TwitchClient(
                configuration.twitch_client_id,
                configuration.twitch_client_secret,
            ),
        }
    
    async def upsert_access_token(
        self,
        service: Origin,
        user_id: str,
        token: OAuthToken,
    ) -> AuthorizationToken:
        encrypted = Encrypted(self.configuration.aes_encryption_key)
        expires_at = pendulum.now().add(seconds=token.expires_in)
        access_token = encrypted.encrypt(token.access_token)
        refresh_token = encrypted.encrypt(token.refresh_token)

        existing_token = (
            await AuthorizationToken
                .filter(user_id=user_id, origin=service)
                .first()
        )

        if not existing_token:
            existing_token = await AuthorizationToken(
                user_id=user_id,
                origin=service,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )

        existing_token.access_token = access_token
        existing_token.refresh_token = refresh_token
        existing_token.expires_at = expires_at

        await existing_token.save()
        return existing_token

    async def get_access_token(self, service: Origin, user_id: str) -> str | None:
        expire_ts = pendulum.now().add(seconds=REDUCED_EXPIRATION)
        client = self.client_mapping.get(service)

        if not client:
            logger.error(
                f"Requested access token for unknown service: {service}",
                extra={
                    "service": service,
                    "user_id": user_id,
                },
            )

            return None
        
        async with in_transaction():
            token = (
                await AuthorizationToken
                    .filter(user_id=user_id, origin=service)
                    .select_for_update() # lock the row
                    .first()
            )

            if not token or token.invalid_token:
                return None

            # if the token is not expired (and won't expire in the next minute)
            if token.expires_at > expire_ts:
                return token.access_token
            
            try:
                new_token: OAuthToken = await client.refresh_token(token.refresh_token)
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (400, 401):
                    token.invalid_token = True

                    await token.save()
                else:
                    logger.exception(
                        f"An error occurred while refreshing token: {e}",
                        extra={
                            "error": e,
                            "token_id": token.id,
                            "user_id": user_id,
                        },
                    )
                
                return None
            
            encrypted = Encrypted(self.configuration.aes_encryption_key)
            access_token = encrypted.encrypt(new_token.access_token)
            refresh_token = encrypted.encrypt(new_token.refresh_token)

            token.access_token = access_token
            token.refresh_token = refresh_token
            token.expires_at = pendulum.now().add(seconds=new_token.expires_in)

            await token.save()
            return new_token.access_token
