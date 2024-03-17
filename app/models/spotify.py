from pydantic import BaseModel


class Device(BaseModel):
    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int
    supports_volume: bool


class Artist(BaseModel):
    name: str


class Album(BaseModel):
    name: str


class Track(BaseModel):
    name: str
    album: Album
    artists: list[Artist]
    uri: str


class CurrentlyPlaying(BaseModel):
    currently_playing_type: str
    is_playing: bool
    item: Track
