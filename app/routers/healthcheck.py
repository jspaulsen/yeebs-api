from fastapi.responses import JSONResponse
from tortoise import connections, BaseDBAsyncClient

from app.api import api


@api.get("/healthcheck")
async def healthcheck():
    try:
        connection: BaseDBAsyncClient = connections.get("default")

        # We don't care about the result, just that the connection and query succeed
        await connection.execute_query("SELECT 1")
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message":"Unhealthy", "exception": str(e)}
        )
    
    return JSONResponse(
        status_code=200, 
        content={"status": "ok"}
    )

