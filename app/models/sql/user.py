from tortoise import Tortoise, fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    external_user_id = fields.CharField(max_length=255, unique=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "application_user"