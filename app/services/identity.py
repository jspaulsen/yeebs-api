import secrets
import pendulum
from tortoise.transactions import in_transaction

from app.configuration import Configuration
from app.identity.jwt import AccessToken, Jwt, JwtHeader, JwtPayload
from app.models.sql.refresh_token import RefreshToken
from app.models.sql.user import User


def random_refresh_token() -> str:
    return secrets.token_urlsafe(32)


class Identity:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    async def create_access_token(self, user: User) -> AccessToken:
        old_token = await RefreshToken.get_or_none(user_id=user.id)

        # if the user already has a refresh token, we should invalidate it
        if old_token:
            old_token.invalidated_at = pendulum.now()
            await old_token.save()

        new_refresh_token = RefreshToken(
            user_id=user.id,
            refresh_token=random_refresh_token(),
        )

        await new_refresh_token.save()

        jwt = Jwt.construct_jwt(
            user.id,
            user.username,
            self.configuration.jwt_expiration,
        )

        return AccessToken(
            access_token=jwt.encode(self.configuration.jwt_secret_key),
            refresh_token=new_refresh_token.refresh_token,
            expires_in=self.configuration.jwt_expiration,
            scope=self.configuration.twitch_scope,
            token_type="bearer",
        )
    

    async def refresh_token(self, refresh_token: str) -> AccessToken | None:
        old_token = await RefreshToken.get(refresh_token=refresh_token)

        if not old_token or old_token.invalidated_at:
            return None
        
        user = await User.get_or_none(id=old_token.user_id)

        if not user:
            return None
        
        with await in_transaction():
            new_refresh_token = RefreshToken(
                user_id=user.id,
                refresh_token=random_refresh_token(),
            )

            old_token.invalidated_at = pendulum.now()

            await new_refresh_token.save()
            await old_token.save()
        
        jwt = Jwt.construct_jwt(
            user.id, 
            user.username, 
            self.configuration.jwt_expiration,
        )

        return AccessToken(
            access_token=jwt.encode(self.configuration.jwt_secret_key), 
            refresh_token=new_refresh_token.refresh_token,
            expires_in=self.configuration.jwt_expiration,
            scope=self.configuration.twitch_scope,
            token_type="bearer",
        )