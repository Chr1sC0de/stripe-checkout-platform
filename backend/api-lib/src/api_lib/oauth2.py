import time
from typing import Literal, Optional, Annotated, Dict

import requests
from fastapi import HTTPException, Depends, Form
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from api_lib import utils

router = APIRouter()

cognito_domain_url = utils.get_ssm_parameter_value(
    utils.SSMParameterName.SSM_COGNITO_DOMAIN_URL.value
)

cognito_authorize_url = f"{cognito_domain_url}/oauth2/authorize"
cognito_revoke_url = f"{cognito_domain_url}/oauth2/revoke"
cognito_token_url = f"{cognito_domain_url}/oauth2/token"

client_id = utils.get_ssm_parameter_value(
    utils.SSMParameterName.USER_POOL_CLIENT_ID.value
)

api_url = None

token_redirect_uri = (
    "https://0.0.0.0:8000/docs"
    if utils.DEVELOPMENT_LOCATION == "local"
    else f"{api_url}docs"
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/oauth2/authorize",
    tokenUrl="/oauth2/token",
)


class TokenResponse(BaseModel):
    id_token: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


@router.post("/revoke")
async def revoke(token: str):
    response = requests.post(
        cognito_revoke_url,
        data={"token": token, "client_id": client_id},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.text


@router.get("/authorize")
async def authorize(
    request: Request,
    state: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    identity_provider: Optional[
        Literal["Facebook", "Google", "LoginWithAmazon", "SignInWithApple"]
    ] = None,
):
    url = f"{cognito_authorize_url}?response_type=code&client_id={client_id}&redirect_uri={token_redirect_uri if redirect_uri is None else redirect_uri}"
    if identity_provider is not None:
        url += f"&identity_provider={identity_provider}"
    if state is not None:
        url += f"&state={state}"
    return RedirectResponse(url=url)


@router.post("/token")
async def token_authorization_code(
    grant_type: Annotated[Literal["authorization_code", "refresh_token"], Form()],
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
) -> TokenResponse:
    if not code:
        return HTTPException(status_code=400, detail="Invalid callback request")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    max_retries = 3
    retries = 0

    while retries < max_retries:
        response = requests.post(
            cognito_token_url,
            data={
                k: v
                for k, v in {
                    "grant_type": grant_type,
                    "code": code,
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "refresh_token": refresh_token,
                }.items()
                if v is not None
            },
            headers=headers,
        ).json()

        if "id_token" in response:
            token_response = TokenResponse(**response)
            break

        time.sleep(2**retries)

        retries += 1

        if retries >= max_retries:
            return HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=response,
            )

    if not utils.verify_jwt(token_response.access_token):
        return HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unverified JWT",
        )

    return token_response


class TokenValidationResponse(BaseModel):
    valid: bool
    description: str


@router.post("/validate-token")
async def validate_token(token: Annotated[str, Depends(oauth2_scheme)]):
    if not utils.verify_jwt(token):
        return TokenValidationResponse(valid=False, description="invalid token")
    return TokenValidationResponse(valid=True, description="valid token")


async def validate_bearer(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenResponse:
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No token provided",
        )

    if not utils.verify_jwt(token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return token


@router.get("/test")
async def help(token: Annotated[TokenResponse, Depends(validate_bearer)]):
    return JSONResponse(content={"message": "yeah boi"})
