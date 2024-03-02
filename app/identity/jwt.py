from __future__ import annotations
import json
from typing import Self

from joserfc import jwt, errors
import pendulum
from pydantic import BaseModel


class TokenException(Exception):
    pass


class JwtHeader(BaseModel):
    alg: str = "HS256"
    typ: str = "JWT"


class JwtPayload(BaseModel):
    user_id: int
    username: str
    iat: int
    exp: int


class Jwt(BaseModel):
    header: JwtHeader
    claims: JwtPayload

    @classmethod
    def construct_jwt(cls, user_id: int, username: str, expires_in: int) -> Jwt:
        now = pendulum.now(tz="UTC")

        return cls(
            header=JwtHeader(),
            claims=JwtPayload(
                user_id=user_id,
                username=username,
                iat=now.int_timestamp,
                exp=now.add(seconds=expires_in).int_timestamp,
            ),
        )
    
    def encode(self, secret: str) -> str:
        return jwt.encode(
            self.header.model_dump(),
            self.claims.model_dump(),
            secret,
        )
    
    @classmethod
    def decode(cls, token: str, secret: str) -> Jwt:
        try:
            decoded_jwt = jwt.decode(token, secret)
        except errors.JoseError as e:
            raise TokenException(
                f" Invalid token: {e}",
            ) from e

        return cls(
            header=JwtHeader(**decoded_jwt.header),
            claims=JwtPayload(**decoded_jwt.claims),
        )


class AccessToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    scope: list[str]
    token_type: str

    @classmethod
    def from_json(cls, token: str) -> Self:
        try:
            return cls(
                **json.loads(
                    token,
                ),
            )
        except json.JSONDecodeError as e:
            raise TokenException(
                f"Invalid token: {e}",
            ) from e
