import abc
from typing import Any

from app.models.oauth_token import OAuthToken


class OAuthClient(abc.ABC):
    @abc.abstractmethod
    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        pass
