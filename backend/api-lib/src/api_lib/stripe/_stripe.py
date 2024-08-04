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
from api_lib.stripe import schemas, tables

router = APIRouter()


# ---------------------------------------------------------------------------- #
#                              protected endpoints                             #
# ---------------------------------------------------------------------------- #


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


@router.get("/current-user-past-purchases")
async def get_current_user_past_purchase(
    access_token: Annotated[str, Depends(oauth2.validate_bearer)],
):
    cognito_client = general_utils.get_client("cognito-idp")
    dynamodb_client = general_utils.get_client(service_name="dynamodb")

    customer_id = [
        v
        for v in cognito_client.get_user(AccessToken=access_token)["UserAttributes"]
        if v["Name"] == "custom:stripe_customer_id"
    ][0]["Value"]

    products = {
        s["id"]: s for s in stripe_utils.get_table_items(tables.PRODUCT_TABLE_NAME)
    }

    output = []

    def process_list_item(item):
        created_date = item["created"]
        for l in item["line_items"]:
            l["created"] = created_date

        return item["line_items"]

    [
        output.extend(process_list_item(i))
        for i in stripe_utils.query_and_extract_items_from_statement(
            dynamodb_client,
            f"""select created, line_items from "{tables.CHECKOUT_SESSION_COMPLETE_TABLE}" where customer='{customer_id}'""",
        )
    ]

    output = [
        {c: o[c] for c in ["quantity", "price", "created", "currency"]} for o in output
    ]
    for o in output:
        o["product"] = o["price"]["product"]
        o["unit_amount"] = o["price"]["unit_amount"]
        o["currency"] = o["price"]["currency"]
        o["created"] = o["price"]["created"]
        if o["product"] in products:
            o["details"] = {n: products[o["product"]][n] for n in ["images", "name"]}
        del o["price"]

    cognito_client.close()
    dynamodb_client.close()
    return output


# ---------------------------------------------------------------------------- #
#                             unprotected endpoints                            #
# ---------------------------------------------------------------------------- #


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


@router.get("/products")
async def get_products(active_only: bool = True) -> List[schemas.Product]:
    return stripe_utils.get_table_items(
        tables.PRODUCT_TABLE_NAME,
        schemas.Product,
    )


@router.get("/prices")
async def get_prices(active_only: bool = True) -> List[schemas.Price]:
    return stripe_utils.get_table_items(
        tables.PRICE_TABLE_NAME,
        schemas.Price,
    )


@router.get("/product-popularity")
async def get_product_popularity() -> List[schemas.RankedProduct]:
    product_counter = {
        p["id"]: ({c: p[c] for c in ["id", "images", "name"]} | {"quantity": 0})
        for p in stripe_utils.get_table_items(
            tables.PRODUCT_TABLE_NAME,
        )
        if p["active"]
    }

    line_items = stripe_utils.get_line_items()

    for item in line_items:
        product_id = item["price"]["product"]
        if product_id in product_counter:
            product_counter[product_id]["quantity"] += int(item["quantity"])

    return list(
        sorted(
            [p for p in product_counter.values()],
            key=lambda x: x["quantity"],
            reverse=True,
        )
    )
