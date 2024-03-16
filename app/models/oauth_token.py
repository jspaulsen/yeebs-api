from pydantic import BaseModel


class OAuthToken(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    scope: list[str] | str
    token_type: str
