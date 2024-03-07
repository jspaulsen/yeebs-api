from tortoise import fields
from tortoise.models import Model


class ApiToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="api_token")
    token = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    invalidated_at = fields.DatetimeField(null=True)


    class Meta:
        table = "api_token"
