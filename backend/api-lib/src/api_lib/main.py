from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from api_lib import oauth2, user, utils, stripe


app = FastAPI()

if utils.DEVELOPMENT_LOCATION == "local":
    from fastapi.middleware.cors import CORSMiddleware

    origins = ["https://0.0.0.0:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type", "Authorization"],
    )


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "DEVELOPMENT_LOCATION": utils.DEVELOPMENT_LOCATION,
            "DEVELOPMENT_ENVIRONMENT": utils.DEVELOPMENT_ENVIRONMENT,
        }
    )


app.include_router(oauth2.router, prefix="/oauth2")
app.include_router(
    user.router, prefix="/user", dependencies=[Depends(oauth2.validate_bearer)]
)
app.include_router(stripe.router, prefix="/stripe")
