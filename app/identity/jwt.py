from __future__ import annotations

from joserfc import jwt
import pendulum
from pydantic import BaseModel



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
        decoded_jwt = jwt.decode(token, secret)

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