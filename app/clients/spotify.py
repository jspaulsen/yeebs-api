from base64 import b64encode

from cachetools import cached, TTLCache
import httpx
from pydantic import BaseModel

from app.models.oauth_token import OAuthToken
from app.clients.oauth_client import OAuthClient
from app.models.spotify import CurrentlyPlaying, Track, Device


TTL_CACHE = TTLCache(maxsize=1024, ttl=300)


class AvailableDevicePayload(BaseModel):
    devices: list[Device]

    @property
    def active_device(self) -> Device | None:
        return next((device for device in self.devices if device.is_active), None)


class QueuePayload(BaseModel):
    currently_playing: Track
    queue: list[Track]


class SearchTracks(BaseModel):
    items: list[Track]


class SearchPayload(BaseModel):
    tracks: SearchTracks
    

class SpotifyClient(OAuthClient):
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
        url = "https://accounts.spotify.com/api/token"

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
        url = "https://accounts.spotify.com/api/token"
        auth = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        data = {
            # "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth}",
                },
                data=data,
                timeout=4,
            )

            response.raise_for_status()
            return OAuthToken(**response.json())
    
    @cached(TTL_CACHE)
    async def get_available_devices(self, access_token: str) -> AvailableDevicePayload:
        url = "https://api.spotify.com/v1/me/player/devices"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
    
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return AvailableDevicePayload(**response.json())

    async def get_current_song(self, access_token: str, device_id: str) -> CurrentlyPlaying:
        url = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return CurrentlyPlaying(**response.json())
    
    async def get_next_songs(self, access_token: str, device_id: str) -> QueuePayload:
        url = "https://api.spotify.com/v1/me/player/queue"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return QueuePayload(**response.json())
    
    async def pause_song(self, access_token: str) -> None:
        url = "https://api.spotify.com/v1/me/player/pause"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers)
            response.raise_for_status()

    async def resume_song(self, access_token: str) -> None:
        url = "https://api.spotify.com/v1/me/player/play"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers)
            response.raise_for_status()

    async def skip_song(self, access_token: str) -> None:
        url = "https://api.spotify.com/v1/me/player/next"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
    
    async def search_songs(self, access_token: str, query: str) -> SearchPayload:
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        query_params = {
            "q": query,
            "type": "track,artist,album",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()

            return SearchPayload(**response.json())
    
    async def get_track(self, access_token: str, track_id: str) -> Track:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return Track(**response.json())
    
    async def enqueue_song(self, access_token: str, uri: str) -> None:
        url = "https://api.spotify.com/v1/me/player/queue"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                headers=headers, 
                params={"uri": uri},
            )
            
            response.raise_for_status()
