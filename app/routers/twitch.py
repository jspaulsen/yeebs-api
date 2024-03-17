from enum import StrEnum
from typing import Annotated

from fastapi import Request, Response, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.clients.twitch import EventSubSubscription, TwitchClient
from app.configuration import Configuration
from app.identity.jwt import Jwt, jwt_dependency
from app.models.sql.user import User
from app.models.twitch import ChannelChatMessageSubscriptionCondition, EventType, TransportMethod

from app.routers import twitch_router


class TwitchEventSubSubscription(BaseModel):
    id: str
    status: str
    type: str # TODO: Enum
    version: str
    cost: int
    condition: dict # TODO: TwitchEventSubCondition
    transport: dict # TODO: TwitchEventSubTransport
    created_at: str


class TwitchEventSubEvent(BaseModel): # TODO: this will be different depending on the type
    user_id: str
    user_login: str
    user_name: str
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str
    followed_at: str


class TwitchEventSubNotification(BaseModel):
    subscription: TwitchEventSubSubscription
    event: TwitchEventSubEvent


class TwitchEventSubChallenge(BaseModel):
    challenge: str
    subscription: dict


class TwitchEventSubRevocation(BaseModel):
    subscription: dict


class TwitchEventSubMessageType(StrEnum):
    WEBHOOK_CALLBACK_VERIFICATION = "webhook_callback_verification"
    NOTIFICATION = "notification"
    REVOCATION = "revocation"


@twitch_router.post("/webhook")
async def twitch_webhook(request: Request):
    event_type = TwitchEventSubMessageType(request.headers.get("twitch-eventsub-message-type"))
    body = await request.json()
    response = None

    match event_type:
        # TODO: Check the signature
        case TwitchEventSubMessageType.WEBHOOK_CALLBACK_VERIFICATION:
            challenge = TwitchEventSubChallenge(**body)

            response = Response(
                content=challenge.challenge,
                media_type="text/plain",
            )

        # TODO: Handle the event
        case TwitchEventSubMessageType.NOTIFICATION:
            notification = TwitchEventSubNotification(**body)

            print(notification)

            response = Response(
                content="",
                media_type="text/plain",
            )
        
        # TODO: Handle the revocation
        case TwitchEventSubMessageType.REVOCATION:
            print(TwitchEventSubRevocation(**body))

            response = Response(
                content="",
                media_type="text/plain",
            )

    return response


@twitch_router.get("/subscribe-me-bitch")
async def subscribe_me(request: Request, jwt: Annotated[Jwt, Depends(jwt_dependency)]) -> Response:
    configuration: Configuration = request.app.state.configuration
    client = TwitchClient(
        configuration.twitch_client_id, 
        configuration.twitch_client_secret,
    )

    user: User = await User.get(id=jwt.claims.user_id)

    event = EventSubSubscription(
        type=EventType.CHANNEL_CHAT_MESSAGE,
        condition=ChannelChatMessageSubscriptionCondition(
            user_id=user.external_user_id,
            broadcaster_user_id=user.external_user_id,
        ),
        transport=TransportMethod(
            callback='https://api.yeebs.dev/twitch/webhook',
            secret='aaaaaaaaaaaaaaasdasdasdasdad',
        ),
    )
    
    result = await client.subscribe_to_event(event)

    return JSONResponse(
        content=result.model_dump(),
        status_code=200,
    )

        


