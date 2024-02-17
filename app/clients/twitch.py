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

    # This is a little bit of a deviation from the regular format,
    # but it abstracts multiple api calls into a single function
    jwks: Jwks


class TwitchClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = "https://api.twitch.tv/helix"
    
    def exchange_code_for_token(self, redirect_uri: str, code: str) -> dict:
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
        return response.json()

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
    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_openid_configuration() -> TwitchOpenIdConfiguration:
        url = "https://id.twitch.tv/oauth2/.well-known/openid-configuration"

        response = requests.get(url)
        response.raise_for_status()

        openid_configuration = TwitchOpenIdConfiguration(**response.json())

        # Call for the jwks and cache it
        response = requests.get(openid_configuration.jwks_uri)
        response.raise_for_status()

        openid_configuration.jwks = Jwks(**response.json())
        return openid_configuration


# {"keys":[{"alg":"RS256","e":"AQAB","kid":"1","kty":"RSA","n":"6lq9MQ-q6hcxr7kOUp-tHlHtdcDsVLwVIw13iXUCvuDOeCi0VSuxCCUY6UmMjy53dX00ih2E4Y4UvlrmmurK0eG26b-HMNNAvCGsVXHU3RcRhVoHDaOwHwU72j7bpHn9XbP3Q3jebX6KIfNbei2MiR0Wyb8RZHE-aZhRYO8_-k9G2GycTpvc-2GBsP8VHLUKKfAs2B6sW3q3ymU6M0L-cFXkZ9fHkn9ejs-sqZPhMJxtBPBxoUIUQFTgv4VXTSv914f_YkNw-EjuwbgwXMvpyr06EyfImxHoxsZkFYB-qBYHtaMxTnFsZBr6fn8Ha2JqT1hoP7Z5r5wxDu3GQhKkHw","use":"sig"}]}
# https://id.twitch.tv/oauth2/.well-known/openid-configuration
# {"authorization_endpoint":"https://id.twitch.tv/oauth2/authorize","claims_parameter_supported":true,"claims_supported":["aud","exp","iat","email_verified","preferred_username","updated_at","iss","sub","azp","email","picture"],"id_token_signing_alg_values_supported":["RS256"],"issuer":"https://id.twitch.tv/oauth2","jwks_uri":"https://id.twitch.tv/oauth2/keys","response_types_supported":["id_token","code","token","code id_token","token id_token"],"scopes_supported":["openid"],"subject_types_supported":["public"],"token_endpoint":"https://id.twitch.tv/oauth2/token","token_endpoint_auth_methods_supported":["client_secret_post"],"userinfo_endpoint":"https://id.twitch.tv/oauth2/userinfo"}