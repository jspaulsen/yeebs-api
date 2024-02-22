import freezegun
import pendulum
import pytest
from app.configuration import Configuration
from app.identity.jwt import AccessToken, Jwt
from app.models.encrypted import Encrypted
from app.models.sql.refresh_token import RefreshToken

from app.services.identity import Identity


class TestIdentity:
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    @pytest.mark.asyncio(scope="session")
    async def test_create_access_token(self, setup_user):
        configuration = Configuration()
        identity = Identity(configuration)

        now = pendulum.now()
        
        old_token = await RefreshToken.create(
            user_id=setup_user.id,
            refresh_token="old_token",
            refresh_token_hash="old_token_hash",
        )

        tokens: AccessToken = await identity.create_access_token(setup_user)

        # check the access token; we'll need to decode it
        decoded_token = Jwt.decode(
            tokens.access_token, 
            configuration.jwt_secret_key,
        )

        assert decoded_token.claims.user_id == setup_user.id
        assert decoded_token.claims.username == setup_user.username
        assert decoded_token.claims.exp == now.add(seconds=configuration.jwt_expiration).int_timestamp
        assert tokens.expires_in == configuration.jwt_expiration

    @pytest.mark.asyncio
    async def test_refresh_token(self, setup_user):
        configuration = Configuration()
        identity = Identity(configuration)
        encrypted = Encrypted(configuration.aes_encryption_key)
        old_token_hash = encrypted.hash("old_token")

        old_token = await RefreshToken.create(
            user_id=setup_user.id,
            refresh_token="old_token",
            refresh_token_hash=old_token_hash,
        )

        tokens: AccessToken = await identity.refresh_token("old_token")

        assert tokens.refresh_token != "old_token"
        assert tokens.expires_in == configuration.jwt_expiration
        assert tokens.scope == configuration.twitch_scope
        assert tokens.token_type == "bearer"
