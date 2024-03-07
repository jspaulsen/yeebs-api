from fastapi import APIRouter

oauth_router = APIRouter(prefix="/oauth")

# Import the routes for the router after the router is defined
from app.routers.oauth.twitch import twitch_oauth_callback, twitch_oauth_redirect
from app.routers.oauth.spotify import spotify_oauth_callback, spotify_oauth_redirect
