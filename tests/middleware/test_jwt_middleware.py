# @api.middleware("http")
#async def jwt_middleware(request: Request, call_next: Any) -> Response:

import freezegun
import pytest

from app.configuration import Configuration
from app.identity.jwt import AccessToken, Jwt
from app.middleware.jwt_middleware import jwt_middleware
from app.services.identity import Identity


class TestJwtMiddleware:
    @pytest.mark.asyncio
    async def test_jwt_middleware(self, mocker, setup_user):
        request = mocker.Mock()
        response = mocker.Mock()

        async def call_next(request):
            return response
        
        async def refresh_token(refresh_token):
            return AccessToken(
                access_token="new_access_token",
                refresh_token="new_refresh_token",
                expires_in=3600,
                scope=["user:read:email"],
                token_type="bearer",
            )
        
        mocked_identity = mocker.patch.object(
            Identity,
            "refresh_token",
            side_effect=refresh_token,
        )

        configuration = Configuration()
        request.app.state.jwt = "some_jwt"
        request.app.state.configuration = configuration
        request.app.state.identity = Identity(configuration)

        with freezegun.freeze_time("2021-01-01"):
            jwt = Jwt.construct_jwt(
                setup_user.id,
                setup_user.username,
                0,
            )

        access_token = AccessToken(
            access_token=jwt.encode(configuration.jwt_secret_key),
            refresh_token="abc123",
            expires_in=-15, #
            scope=["user:read:email"],
            token_type="bearer",
        )

        request.cookies = {"access_token": access_token.model_dump_json()}
        response = await jwt_middleware(request, call_next)

        assert mocked_identity.called
        assert response.set_cookie.called

        assert request.state.jwt
        assert request.state.jwt.claims.user_id == setup_user.id