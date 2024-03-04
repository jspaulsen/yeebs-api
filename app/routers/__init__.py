from fastapi import APIRouter

twitch_router = APIRouter(prefix="/twitch", tags=["twitch"])

from app.routers.twitch import twitch_webhook
