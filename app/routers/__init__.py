from fastapi import APIRouter

twitch_router = APIRouter(prefix="/twitch", tags=["twitch"])
spotify_router = APIRouter(prefix="/spotify", tags=["spotify"])


# Imports the routes for the router after the router is defined
from app.routers.twitch import twitch_webhook
from app.routers.spotify import get_current_song
