from tortoise import fields
from tortoise.models import Model


class RefreshToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="refresh_token")
    refresh_token = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    invalidated_at = fields.DatetimeField(null=True)

    class Meta:
        table = "authorization_token"