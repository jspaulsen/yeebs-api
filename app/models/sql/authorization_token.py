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
    access_token = fields.TextField()
    refresh_token = fields.TextField()
    invalid_token = fields.BooleanField(default=False)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "authorization_token"
