from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api_lib import utils
from api_lib import oauth2

app = FastAPI()


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "DEVELOPMENT_LOCATION": utils.DEVELOPMENT_LOCATION,
            "DEVELOPMENT_ENVIRONMENT": utils.DEVELOPMENT_ENVIRONMENT,
        }
    )


app.include_router(oauth2.router, prefix="/oauth2")
