from tortoise import fields
from tortoise.models import Model


class AuthorizationToken(Model):
    authorization_id = fields.IntField(pk=True)
    user_id = fields.ForeignKeyField("models.User", related_name="authorization_tokens")
    origin = fields.CharField(max_length=255)
    refresh_token = fields.CharField(max_length=255)
    invalid_token = fields.BooleanField(default=False)
    expires_at = fields.DatetimeField()
    refresh_lock = fields.BooleanField(default=False)
    last_refreshed_at = fields.DatetimeField(default=None)

    class Meta:
        table = "authorization_token"