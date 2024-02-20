import freezegun
import httpx
import pendulum
import pytest

from app.services.authorization import Authorization
from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.models.oauth_token import OAuthToken
from app.models.sql.authorization_token import AuthorizationToken, Origin
from app.models.sql.user import User


@pytest.mark.asyncio(scope="class")
class TestAuthorization:
    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_add_access_token(self, setup_user):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)

        setup_user: User = setup_user
        now = pendulum.now()

        oauth_token = OAuthToken(
            access_token="test_access_token",
            expires_in=360,
            refresh_token="test_refresh_token",
            scope=[],
            token_type="bearer",
        )
        
        result = await access_token_manager.upsert_access_token(
            Origin.Twitch,
            setup_user.id,
            oauth_token,
        )

        # Fetch token from database
        db_token = await AuthorizationToken.filter(id=result.id).first()

        assert db_token.user_id == setup_user.id
        assert db_token.origin == Origin.Twitch
        assert db_token.access_token == "test_access_token"
        assert db_token.refresh_token == "test_refresh_token"
        assert db_token.expires_at == now.add(seconds=360)
    
    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_update_access_token(self, setup_user):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)
        setup_user: User = setup_user

        now = pendulum.now()

        # Create a token
        await AuthorizationToken.create(
            user_id=setup_user.id,
            origin=Origin.Twitch,
            access_token="old_access_token",
            refresh_token="old_refresh_token",
            expires_at=now,
        )

        # Update the token
        oauth_token = OAuthToken(
            access_token="new_access_token",
            expires_in=360,
            refresh_token="new_refresh_token",
            scope=[],
            token_type="bearer",
        )

        result = await access_token_manager.upsert_access_token(
            Origin.Twitch,
            setup_user.id,
            oauth_token,
        )

        # Fetch token from database
        db_token = await AuthorizationToken.filter(id=result.id).first()

        assert db_token.user_id == setup_user.id
        assert db_token.origin == Origin.Twitch
        assert db_token.access_token == "new_access_token"
        assert db_token.refresh_token == "new_refresh_token"
        assert db_token.expires_at == now.add(seconds=360)

    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_get_access_token(self, setup_user):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)
        setup_user: User = setup_user

        now = pendulum.now()

        # Create a token
        existing_token = await AuthorizationToken.create(
            user_id=setup_user.id,
            origin=Origin.Twitch,
            access_token="access_token",
            refresh_token="refresh_token",
            expires_at=now + pendulum.duration(seconds=360),
        )

        token = await access_token_manager.get_access_token(Origin.Twitch, setup_user.id)
        assert token == "access_token"

    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_get_access_token_refresh(self, setup_user, mocker):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)
        setup_user: User = setup_user

        now = pendulum.now()

        mocked_client = mocker.patch.object(
            TwitchClient,
            'refresh_token',
            return_value=OAuthToken(
                access_token="new_access_token",
                refresh_token="new_refresh_token",
                expires_in=360,
                scope=[],
                token_type="bearer",
            )
        )

        # Create a token
        existing_token = await AuthorizationToken.create(
            user_id=setup_user.id,
            origin=Origin.Twitch,
            access_token="access_token",
            refresh_token="refresh_token",
            expires_at=now - pendulum.duration(seconds=360), # Expired
        )

        token = await access_token_manager.get_access_token(Origin.Twitch, setup_user.id)

        assert token == "new_access_token"

        assert mocked_client.called
        assert mocked_client.called_with("refresh_token")

        # fetch token from database
        db_token = await AuthorizationToken.filter(id=existing_token.id).first()

        assert db_token.access_token == "new_access_token"
        assert db_token.refresh_token == "new_refresh_token"
        assert db_token.expires_at == now.add(seconds=360)
    
    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_get_access_token_invalid_token(self, setup_user):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)
        setup_user: User = setup_user

        now = pendulum.now()

        # Create a token
        existing_token = await AuthorizationToken.create(
            user_id=setup_user.id,
            origin=Origin.Twitch,
            access_token="access_token",
            refresh_token="refresh_token",
            expires_at=now + pendulum.duration(seconds=1080),
            invalid_token=True,
        )

        token = await access_token_manager.get_access_token(Origin.Twitch, setup_user.id)
        assert token is None

    @pytest.mark.asyncio
    @freezegun.freeze_time("2021-01-01T00:00:00Z")
    async def test_get_access_token_refresh_failed(self, setup_user, mocker):
        configuration = Configuration()
        access_token_manager = Authorization(configuration)
        setup_user: User = setup_user

        now = pendulum.now()

        mocked_client = mocker.patch.object(
            TwitchClient,
            'refresh_token',
            side_effect=httpx.HTTPStatusError(
                message="Fake error",
                request=httpx.Request("GET", "http://localhost"),
                response=httpx.Response(400),
            ),
        )

        # Create a token
        existing_token = await AuthorizationToken.create(
            user_id=setup_user.id,
            origin=Origin.Twitch,
            access_token="access_token",
            refresh_token="refresh_token",
            expires_at=now - pendulum.duration(seconds=1080),
            invalid_token=False,
        )


        token = await access_token_manager.get_access_token(Origin.Twitch, setup_user.id)

        assert token is None
        assert mocked_client.called

        # fetch token from database
        db_token = await AuthorizationToken.filter(id=existing_token.id).first()

        assert db_token.invalid_token



