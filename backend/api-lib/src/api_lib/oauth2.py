import time
from typing import Annotated, Literal, Optional

import requests
from fastapi import Cookie, Depends, Form, HTTPException, Response
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

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

api_url = utils.get_ssm_parameter_value(
    utils.SSMParameterName.SSM_API_FUNCTION_URL.value
)

token_redirect_uri = (
    "https://0.0.0.0:8000/docs"
    if utils.DEVELOPMENT_LOCATION == "local"
    else f"{api_url}docs"
)


class OAuth2AuthorizationCodeBearerWithCookie(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None  # pragma: nocover
        return param


oauth2_scheme = OAuth2AuthorizationCodeBearerWithCookie(
    authorizationUrl="/oauth2/authorize",
    tokenUrl="/oauth2/token",
)


class TokenResponse(BaseModel):
    id_token: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    expires_in: Optional[int]
    token_type: Optional[str]


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
) -> RedirectResponse:
    url = f"{cognito_authorize_url}?response_type=code&client_id={client_id}&redirect_uri={token_redirect_uri if redirect_uri is None else redirect_uri}"
    if identity_provider is not None:
        url += f"&identity_provider={identity_provider}"
    if state is not None:
        url += f"&state={state}"
    return RedirectResponse(url=url)


@router.post("/token")
async def token(
    response: Response,
    grant_type: Annotated[Literal["authorization_code", "refresh_token"], Form()],
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
) -> TokenResponse:
    if not code:
        raise HTTPException(status_code=400, detail="Invalid callback request")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    max_retries = 3
    retries = 0

    while retries < max_retries:
        cognito_response = requests.post(
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

        if "id_token" in cognito_response:
            token_response = TokenResponse(**cognito_response)
            break

        time.sleep(2**retries)

        retries += 1

        if retries >= max_retries:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=cognito_response,
            )

    if not utils.verify_jwt(token_response.access_token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unverified JWT",
        )

    response.set_cookie(
        key="Authorization",
        value=f"Bearer {token_response.access_token}",
        secure=True,
        samesite="None",
    )

    return token_response


class TokenValidationResponse(BaseModel):
    valid: bool
    description: str


async def cookie_token(
    access_token: Annotated[str, Depends(oauth2_scheme)] = Cookie(),
):
    return access_token


async def validate_bearer(
    access_token: Annotated[str, Depends(cookie_token)],
) -> TokenResponse:
    if not access_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No token provided",
        )

    if not utils.verify_jwt(access_token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return access_token
