from typing import Any
from fastapi import Request, Response
import pendulum
from app.api import api
from app.configuration import Configuration
from app.identity.jwt import AccessToken, Jwt, TokenException
from app.services.identity import Identity


@api.middleware("http")
async def jwt_middleware(request: Request, call_next: Any) -> Response:
    configuration: Configuration = request.app.state.configuration
    identity: Identity = request.app.state.identity

    new_access_token: AccessToken | None = None
    now = pendulum.now()
    
    if hasattr(request.state, "jwt"):
        del request.state.jwt
    
    # get the jwt cookie from the request
    access_token_raw = request.cookies.get("access_token")

    if not access_token_raw:
        return await call_next(request)
    
    try:
        access_token: AccessToken = AccessToken.from_json(access_token_raw)
        jwt: Jwt = Jwt.decode(access_token.access_token, configuration.jwt_secret_key)
    except TokenException:
        response: Response = await call_next(request)
        response.delete_cookie("access_token")
        
        return response

    # check the jwt for expiration; if it's expired,
    # try to refresh it
    if jwt.claims.exp < now.int_timestamp:
        new_access_token = await identity.refresh_token(access_token.refresh_token)
        
        # If the refresh token is invalid, we should delete the cookie
        if not new_access_token:
            response: Response = await call_next(request)
            response.delete_cookie("access_token")
            
            return response
        
    # Set request state to the new jwt
    request.state.jwt = jwt
    response: Response = await call_next(request)

    # If we have a new access token, we should set the cookie
    if new_access_token:
        response.set_cookie(
            "access_token",
            new_access_token.access_token,
            max_age=new_access_token.expires_in,
            httponly=True,
            secure=False,
            # samesite="lax",
        )
    
    return response