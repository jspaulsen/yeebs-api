from __future__ import annotations

from joserfc import jwt
from joserfc.jwk import RSAKey
from pydantic import BaseModel
from app.clients.twitch import TwitchOpenIdConfiguration


class TwitchOidcValidator:
    def __init__(
        self,
        openid_configuration: TwitchOpenIdConfiguration,
        client_id: str,
    ) -> None:
        self.openid_configuration = openid_configuration
        self.client_id = client_id

        if not self.openid_configuration.jwks:
            raise ValueError('No valid JWKS found in the OpenID Configuration')
        
        self.keys = [RSAKey(**key) for key in self.openid_configuration.jwks.keys]
        self.registry = jwt.JWTClaimsRegistry(
            iss={"essential": True, "value": openid_configuration.issuer},
            sub={"essential": True},
            aud={"essential": True, "value": client_id},
        )

    def validate_jwt(self, token: str) -> TwitchJwt:
        decoded = jwt.decode(token, self.keys)
        claims = decoded.claims

        # Validate the token; this will raise an exception if the token is invalid
        self.registry.validate(claims)
        return TwitchJwt(**claims)


class TwitchJwt(BaseModel):
    sub: str
    exp: int
    iat: int
    iss: str
    aud: str
    preferred_username: str | None = None