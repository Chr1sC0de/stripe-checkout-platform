import os
from typing import Annotated, Any, Dict, List, Literal, Optional

import stripe
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST

from api_lib import oauth2
from api_lib import utils as general_utils
from api_lib.stripe import utils as stripe_utils

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request) -> Dict[str, Any]:
    if general_utils.DEVELOPMENT_LOCATION == "local":
        webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET_LOCAL"]
    else:
        webhook_secret = general_utils.get_ssm_parameter_value(
            general_utils.SSMParameterName.SSM_STRIPE_WEBHOOK_SECRET.value
        )

    headers = request.headers
    signature = headers["stripe-signature"]

    data = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=data.decode("utf-8"),
            sig_header=signature,
            secret=webhook_secret,
        )
    except ValueError as e:
        print("Error parsing payload: {}".format(str(e)))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

    event_type, *fields = event["type"].split(".")

    response = {"message": f"event type {event['type']} not handled"}

    if event_type in ("product", "price", "customer"):
        response = stripe_utils.process_stripe_crud_event(
            event_data=event,
            table=f"{general_utils.COMPANY}-{general_utils.DEVELOPMENT_ENVIRONMENT}-{event_type}",
            operation=fields[-1],
        )

    if event["type"] == "checkout.session.completed":
        response = stripe_utils.process_checkout_session_completed_event(
            event_data=event
        )

    return response


class PriceItem(BaseModel):
    price: str
    quantity: int


@router.post("/create-checkout-session")
async def create_checkout_session(
    access_token: Annotated[str, Depends(oauth2.validate_bearer)],
    line_items: List[PriceItem],
    return_type: Literal["redirect", "json"] = "json",
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
):
    if (
        general_utils.DEVELOPMENT_LOCATION == "local"
        and success_url is None
        and cancel_url is None
    ):
        domain_url = "https://0.0.0.0:3000"
        success_url = domain_url + "?success=true"
        cancel_url = domain_url + "?success=true"

    client = general_utils.get_client("cognito-idp")

    customer_id = [
        k
        for k in client.get_user(AccessToken=access_token)["UserAttributes"]
        if k["Name"] == "custom:stripe_customer_id"
    ][0]["Value"]

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[p.dict() for p in line_items],
            customer=customer_id,
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=[],
        )
    except Exception as e:
        return str(e)

    if return_type == "redirect":
        return RedirectResponse(url=checkout_session.url)
    elif return_type == "json":
        return JSONResponse(content={"url": f"{checkout_session.url}"})
