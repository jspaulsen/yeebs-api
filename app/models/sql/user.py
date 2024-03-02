from tortoise import fields, Model
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True)
    external_user_id = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=255)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "application_user"
    
    class PydanticMeta:
        exclude = ["id"]


UserModel = pydantic_model_creator(User)