from typing import Annotated, Self
from urllib.parse import urlparse
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.clients.spotify import SpotifyClient
from app.configuration import Configuration
from app.models.spotify import Track
from app.models.sql.api_token import ApiToken
from app.models.sql.authorization_token import Origin

from app.routers import spotify_router
from app.services.authorization import Authorization


class Song(BaseModel):
    album_title: str
    song_title: str
    artists: str

    @classmethod
    def from_currently_playing_item(cls, currently_playing: Track) -> Self:
        return cls(
            album_title=currently_playing.album.name,
            song_title=currently_playing.name,
            artists=", ".join(artist.name for artist in currently_playing.artists),
        )


async def get_api_token(request: Request) -> ApiToken:
    token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    api_token = await ApiToken.get_or_none(token=token)

    if not api_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return api_token


@spotify_router.get("/current-song")
async def get_current_song(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)]) -> Song:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    devices = await spotify_client.get_available_devices(access_token)
    active_device = devices.active_device

    if not active_device:
        return Response(
            status_code=200,
            content={"message": "No active device found"},
        )

    current_song = await spotify_client.get_current_song(
        access_token,
        active_device.id,
    )

    return Song.from_currently_playing_item(current_song.item)


@spotify_router.get("/next-song")
async def get_next_songs(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)]) -> Song:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    devices = await spotify_client.get_available_devices(access_token)
    active_device = devices.active_device

    if not active_device:
        return Response(
            status_code=200,
            content={"message": "No active device found"},
        )

    queue_payload = await spotify_client.get_next_songs(
        access_token,
        active_device.id,
    )

    next_song = next(iter(queue_payload.queue), None)

    if not next_song:
        return Response(
            status_code=404,
            content={"message": "No next song found"},
        )

    return Song.from_currently_playing_item(next_song)


@spotify_router.post("/pause-song")
async def pause(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)]) -> Response:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    devices = await spotify_client.get_available_devices(access_token)
    active_device = devices.active_device

    if not active_device:
        return Response(
            status_code=200,
            content={"message": "No active device found"},
        )

    await spotify_client.pause_song(access_token)
    return Response(status_code=204)

@spotify_router.post("/resume-song")
async def resume(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)]) -> Response:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    devices = await spotify_client.get_available_devices(access_token)
    active_device = devices.active_device

    if not active_device:
        return JSONResponse(
            status_code=200,
            content={"message": "No active device found"},
        )

    await spotify_client.resume_song(access_token)
    return Response(status_code=204)

@spotify_router.post("/skip-song")
async def skip(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)]) -> Response:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    devices = await spotify_client.get_available_devices(access_token)
    active_device = devices.active_device

    if not active_device:
        return Response(
            status_code=200,
            content={"message": "No active device found"},
        )

    await spotify_client.skip_song(access_token)
    return Response(status_code=204)


@spotify_router.get("/search-song")
async def search_songs(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)], query: str) -> Song:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    search_payload = await spotify_client.search_songs(access_token, query)

    first_song = next(iter(search_payload.tracks.items), None)

    if not first_song:
        return JSONResponse(
            status_code=404,
            content={"message": "No songs found"},
        )

    return Song.from_currently_playing_item(first_song)


@spotify_router.post("/enqueue-song")
async def enqueue_song(request: Request, api_token: Annotated[ApiToken, Depends(get_api_token)], song: str) -> Song:
    authorization: Authorization = request.app.state.token_manager
    configuration: Configuration = request.app.state.configuration
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    access_token = await authorization.get_access_token(Origin.Spotify, api_token.user_id)
    track: Track | None = None
    # if the song is a spotify url, parse the url and get the spotify fragment
    # spotify:track:4iV5W9uYEdYUVa79Axb7Rh
    # https://open.spotify.com/track/6kfee9Z4wWfxxPkl2Bxcmd
    if 'http' in song:
        parsed_url = urlparse(song)

        # check that the url is a spotify url
        if 'spotify' not in parsed_url.netloc or 'track' not in parsed_url.path:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid URL"},
            )

        fragment = parsed_url.path.split('/')

        if len(fragment) < 3:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid URL"},
            )
        
        song_id = fragment[-1]
        track = await spotify_client.get_track(access_token, song_id)
    else:
        search_payload = await spotify_client.search_songs(access_token, song)
        track = next(iter(search_payload.tracks.items), None)

        if not track:
            return JSONResponse(
                status_code=404,
                content={"message": "No songs found"},
            )

    # enqueue the song
    await spotify_client.enqueue_song(access_token, track.uri)
    return Song.from_currently_playing_item(track)


