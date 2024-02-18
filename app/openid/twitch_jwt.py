from __future__ import annotations

from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import RSAKey
from joserfc.rfc7519.registry import InvalidClaimError
from pydantic import BaseModel
from app.clients.twitch import TwitchOpenIdConfiguration


class TokenException(InvalidClaimError):
    pass


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
        
        self.keys = [RSAKey.import_key(key) for key in self.openid_configuration.jwks.keys]
        self.registry = jwt.JWTClaimsRegistry(
            iss={"essential": True, "value": openid_configuration.issuer},
            sub={"essential": True},
            aud={"essential": True, "value": client_id},
            leeway=300,
        )

    def validate_jwt(self, token: str) -> TwitchJwt:
        # TODO: We need to select the right key for decoding; for now,
        # we're just using the first key in the list

        try:
            decoded = jwt.decode(token, self.keys[0])
            claims = decoded.claims
            self.registry.validate(claims)
        except JoseError as e:
            raise TokenException from e
        
        return TwitchJwt(**claims)


class TwitchJwt(BaseModel):
    sub: str
    exp: int
    iat: int
    iss: str
    aud: str
    preferred_username: str | None = None