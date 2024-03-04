from pydantic import BaseModel, ConfigDict
import httpx

from app.models.oauth_token import OAuthToken
from app.models.twitch import ChannelChatMessageSubscriptionCondition, EventSubConditionBase, EventType, TransportMethod
from app.clients.oauth_client import OAuthClient


class TokenValidationResponse(BaseModel):
    client_id: str
    login: str
    scopes: list[str]
    user_id: str
    expires_in: int


class ClientCredentials(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


class EventSubSubscriptionA(BaseModel):
    id: str
    status: str
    type: str
    version: str
    condition: dict
    created_at: str
    transport: dict
    cost: int


class EventSubSubscriptionResponse(BaseModel):
    data: list[EventSubSubscriptionA]
    total: int
    total_cost: int
    max_total_cost: int


class EventSubSubscription(BaseModel):
    type: EventType
    version: str = "1"
    condition: EventSubConditionBase
    transport: TransportMethod

    model_config = ConfigDict(
        use_enum_values=True,
        extra='allow',
    )
        


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
                timeout=4,
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
    
    async def get_client_credentials(self) -> ClientCredentials:
        url = "https://id.twitch.tv/oauth2/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )

            response.raise_for_status()
            return ClientCredentials(**response.json())
    
    async def subscribe_to_event(self, subscription: EventSubSubscription) -> EventSubSubscription:
        url = "https://api.twitch.tv/helix/eventsub/subscriptions"

        # get an access token
        client_credentials = await self.get_client_credentials()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {client_credentials.access_token}",
                    "Client-ID": self.client_id,
                },
                json=subscription.model_dump(),
            )

            response.raise_for_status()
            return EventSubSubscription(**response.json())
