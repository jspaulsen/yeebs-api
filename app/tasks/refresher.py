import asyncio
import logging

import pendulum
from tortoise.transactions import in_transaction

from app.clients.oauth_client import OAuthClient
from app.configuration import Configuration
from app.models.oauth_token import OAuthToken
from app.models.sql.authorization_token import AuthorizationToken, Origin
from app.clients.twitch import TwitchClient


logger = logging.getLogger(__name__)


LOCK_DURATION_SECONDS = 25


class RefresherTask:
    def __init__(self, configuration: Configuration, frequency: int) -> None:
        self.frequency = frequency
        self.configuration = configuration

        self.client_mapping = {
            Origin.Twitch: TwitchClient(
                configuration.twitch_client_id,
                configuration.twitch_client_secret,
            ),
        }
    
    async def get_refreshable_tokens(self) -> list[AuthorizationToken]:
        try:
            return await AuthorizationToken.filter(
                expires_at__gt=pendulum.now(),
                expires_at__lt=pendulum.now().add(minutes=5),
                invalid_token=False,
            )
        except Exception as e:
            logger.exception(
                f"An error occurred while fetching refreshable tokens: {e}",
                extra={
                    "error": e,
                },
            )

            return []
    
    async def refresh_tokens(self) -> None:
        refreshable_tokens = await self.get_refreshable_tokens()

        for token in refreshable_tokens:
            client: OAuthClient = self.client_mapping.get(token.origin)

            if not client:
                logger.exception(
                    f"Requested refresh for token with unknown origin: {token.origin}",
                    extra={
                        "token_id": token.id,
                        "origin": token.origin,
                    },
                )

                continue
            
            async with in_transaction():
                try:
                    token = (
                        await AuthorizationToken
                            .filter(id=token.id)
                            .select_for_update()
                            .first()
                    )

                    new_token: OAuthToken = await client.refresh_token(token.refresh_token)

                    token.refresh_token = new_token.refresh_token
                    token.expires_at = pendulum.now().add(seconds=new_token.expires_in - 60)
                    await token.save()
                except Exception as e:
                    logger.exception(
                        f"An error occurred while refreshing token: {e}",
                        extra={
                            "error": e,
                            "token_id": token.id,
                        },
                    )

    async def run(self) -> None:
        while True: # TODO: Add a way to stop this task, e.g. a flag
            await self.refresh_tokens()
            await asyncio.sleep(self.frequency)
