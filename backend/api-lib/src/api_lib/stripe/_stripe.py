import os
from typing import List, Literal

import stripe
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST

from api_lib import utils as general_utils
from api_lib.stripe import utils as stripe_utils

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request):
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

    if event_type in ("product", "price"):
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
    line_items: List[PriceItem], return_type: Literal["redirect", "json"] = "json"
):
    if general_utils.DEVELOPMENT_LOCATION == "local":
        domain_url = "https://0.0.0.0:3000"

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[p.dict() for p in line_items],
            mode="payment",
            success_url=domain_url + "?success=true",
            cancel_url=domain_url + "?canceled=true",
            payment_method_types=[],
        )
    except Exception as e:
        return str(e)

    if return_type == "redirect":
        return RedirectResponse(url=checkout_session.url)
    elif return_type == "json":
        return JSONResponse(content={"url": f"{checkout_session.url}"})
