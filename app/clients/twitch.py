from pydantic import BaseModel
import httpx

from app.models.oauth_token import OAuthToken
from app.clients.oauth_client import OAuthClient


class TokenValidationResponse(BaseModel):
    client_id: str
    login: str
    scopes: list[str]
    user_id: str
    expires_in: int


class TwitchClient(OAuthClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://api.twitch.tv/helix"
        self.client = httpx.AsyncClient()
    
    async def exchange_code_for_token(self, redirect_uri: str, code: str) -> OAuthToken:
        url = "https://id.twitch.tv/oauth2/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data,
            )

            response.raise_for_status()
            return OAuthToken(**response.json())

    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        url = "https://id.twitch.tv/oauth2/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data,
            )

            response.raise_for_status()
            return response.json()
        
    async def validate_token(self, token: str) -> TokenValidationResponse:
        url = "https://id.twitch.tv/oauth2/validate"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )

            response.raise_for_status()
            return TokenValidationResponse(**response.json())