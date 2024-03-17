from typing import Annotated
from fastapi import Depends, Response
from fastapi.responses import JSONResponse
from app.api import api
from app.identity.jwt import Jwt, jwt_dependency
from app.models.sql.user import User, UserModel


@api.get("/userinfo")
async def userinfo(jwt: Annotated[Jwt, Depends(jwt_dependency)]) -> UserModel: # type: ignore
    user: User = await User.get_or_none(id=jwt.claims.user_id)

    if not user:
        return Response(status_code=404, content="User not found")
    
    return await UserModel.from_tortoise_orm(user)

