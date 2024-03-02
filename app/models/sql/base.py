from tortoise import Model
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel


class BaseModel(Model):
    _model_creator_cache = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._model_creator_cache:
            cls._model_creator_cache[cls] = pydantic_model_creator(cls)

        cls._internal_pydantic = cls._model_creator_cache[cls]
        return super().__new__(cls)

    async def to_pydantic_type(self) -> PydanticModel:
        model: type[PydanticModel] = self.__class__._model_creator_cache[self.__class__]
        return await model.from_tortoise_orm(self)