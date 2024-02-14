from fastapi.responses import JSONResponse
from tortoise import Tortoise

from app.api import api


@api.get("/healthcheck")
async def healthcheck():
    try:
        connection = await Tortoise.get_connection("default")

        # We don't care about the result, just that the connection and query succeed
        await connection.execute_query_dict("SELECT 1")
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message":"Unhealthy"}
        )

