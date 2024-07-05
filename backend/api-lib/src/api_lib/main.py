from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api_lib import utils
from api_lib import oauth2

app = FastAPI()


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "RUNTIME_LOCATION": utils.RUNTIME_ENVIRONMENT,
            "RUNTIME_ENVIRONMENT": utils.RUNTIME_LOCATION,
        }
    )


app.include_router(oauth2.router, prefix="/oauth2")
