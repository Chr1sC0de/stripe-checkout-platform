import os

import stripe
from fastapi import Request, HTTPException
from fastapi.routing import APIRouter
from starlette.status import HTTP_400_BAD_REQUEST

from api_lib import utils

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request):
    if utils.DEVELOPMENT_LOCATION == "local":
        webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET_LOCAL"]
    else:
        webhook_secret = utils.get_ssm_parameter_value(
            utils.SSMParameterName.SSM_STRIPE_WEBHOOK_SECRET.value
        )

    headers = request.headers
    signature = headers["stripe-signature"]

    data = await request.body()

    try:
        event_data = stripe.Webhook.construct_event(
            payload=data.decode("utf-8"),
            sig_header=signature,
            secret=webhook_secret,
        )
    except ValueError as e:
        print("Error parsing payload: {}".format(str(e)))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

    kind, *fields = event_data["type"].split(".")

    response = {"message": f"event type {event_data['type']} not handled"}

    table_name = f"{utils.COMPANY}-{utils.DEVELOPMENT_ENVIRONMENT}-{kind}-table"

    if kind in ("product", "price"):
        response = utils.process_stripe_single_field_event(
            event_data, table_name, kind, fields[0]
        )

    return response
