import time
from typing import Literal, Optional

import requests
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
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

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/oauth2/authorize",
    tokenUrl="/oauth2/token/callback",
)


token_redirect_uri = (
    "https://0.0.0.0:8000/oauth2/token/callback"
    # if utils.RUNTIME_LOCATION == "local"
    # else f"{api_url}oauth2/token/callback"
)


class Token(BaseModel):
    id_token: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


@router.get("/authorize")
async def authorize(
    redirect_uri: Optional[str] = None,
    identity_provider: Optional[
        Literal["Facebook", "Google", "LoginWithAmazon", "SignInWithApple"]
    ] = None,
):
    url = f"{cognito_authorize_url}?response_type=code&client_id={client_id}&redirect_uri={token_redirect_uri if redirect_uri is None else redirect_uri}"
    if identity_provider is not None:
        url += f"&identity_provider={identity_provider}"
    return RedirectResponse(url=url)


@router.post("/revoke")
async def revoke(token: str):
    response = requests.post(
        cognito_revoke_url,
        data={"token": token, "client_id": client_id},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.text


oaut2_callback_url = "/token/callback"


@router.get(oaut2_callback_url)
async def token(request: Request) -> Token:
    code = request.query_params.get("code")

    if not code:
        return HTTPException(status_code=400, detail="Invalid callback request")

    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": token_redirect_uri,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    max_retries = 3
    retries = 0

    while retries < max_retries:
        response = requests.post(cognito_token_url, data=data, headers=headers).json()

        if "id_token" in response:
            token_response = Token(**response)
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
