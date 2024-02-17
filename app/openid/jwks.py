from pydantic import BaseModel


class Jwks(BaseModel):
    keys: list[dict]