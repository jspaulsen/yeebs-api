from cachetools import TTLCache, cached
from pydantic import BaseModel
import requests

from app.openid.jwks import Jwks


class TwitchOpenIdConfiguration(BaseModel):
    authorization_endpoint: str
    claims_parameter_supported: bool
    claims_supported: list[str]
    id_token_signing_alg_values_supported: list[str]
    issuer: str
    jwks_uri: str
    response_types_supported: list[str]
    scopes_supported: list[str]
    subject_types_supported: list[str]
    token_endpoint: str
    token_endpoint_auth_methods_supported: list[str]
    userinfo_endpoint: str

    # This is a deviation from the regular format,
    # but it abstracts multiple api calls into a single call
    jwks: Jwks


class TwitchToken(BaseModel):
    access_token: str
    expires_in: int
    id_token: str
    refresh_token: str
    scope: list[str]
    token_type: str


class TwitchClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://api.twitch.tv/helix"
    
    def exchange_code_for_token(self, redirect_uri: str, code: str) -> TwitchToken:
        url = "https://id.twitch.tv/oauth2/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        response = requests.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )

        response.raise_for_status()
        return TwitchToken(**response.json())

    def refresh_token(self, refresh_token: str) -> dict:
        url = "https://id.twitch.tv/oauth2/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        response = requests.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )

        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_openid_configuration() -> TwitchOpenIdConfiguration:
        url = "https://id.twitch.tv/oauth2/.well-known/openid-configuration"

        oidc_response = requests.get(url)
        oidc_response.raise_for_status()
        oidc_json = oidc_response.json()

        # Call for the jwks and cache it
        jwks_response = requests.get(oidc_json.get("jwks_uri"))
        jwks_response.raise_for_status()

        openid_configuration = TwitchOpenIdConfiguration(
            **oidc_response.json(),
            jwks=Jwks(**jwks_response.json()),
        )

        return openid_configuration