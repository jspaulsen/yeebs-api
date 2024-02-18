from enum import StrEnum
from tortoise import fields
from tortoise.models import Model


class Origin(StrEnum):
    Twitch = "twitch"
    Spotify = "spotify"


class AuthorizationToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="authorization_token")
    origin = fields.CharEnumField(Origin)
    refresh_token = fields.CharField(max_length=255)
    invalid_token = fields.BooleanField(default=False)
    refresh_lock = fields.DatetimeField(default=None)
    last_refreshed_at = fields.DatetimeField(default=None)

    class Meta:
        table = "authorization_token"