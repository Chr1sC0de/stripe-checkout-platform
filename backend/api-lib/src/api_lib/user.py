from typing import Annotated, List, Literal, Optional, Dict, Any

from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel
import stripe

from api_lib import oauth2, utils

router = APIRouter()


class UserAttribute(BaseModel):
    Name: str
    Value: str


class MFAOption(BaseModel):
    DeliveryMedium: str
    AttributeName: str


class UserResponse(BaseModel):
    Username: str
    UserAttributes: List[UserAttribute]
    ResponseMetadata: Dict[str, Any]
    MFAOptions: Optional[List[MFAOption]] = None
    PreferredMfaSetting: Optional[str] = None
    UserMFASettingList: Optional[List[Literal["SMS_MFA", "SOFTWARE_TOKEN_MFA"]]] = None


@router.get("")
async def get_user(
    access_token: Annotated[str, Depends(oauth2.validate_bearer)],
) -> UserResponse:
    client = utils.get_client("cognito-idp")

    user_details = client.get_user(AccessToken=access_token)

    # TODO
    # user_attributes = utils.parse_user_attributes(user_details)

    # if "custom:stripe_customer_id" not in user_attributes:
    #     stripe_customer_id = stripe.Customer.create()
    #     client.update_user_attributes(
    #         AccessToken=access_token,
    #         UserAttributes=[
    #             {"Name": "custom:stripe_customer_id", "Value": stripe_customer_id["id"]}
    #         ],
    #     )
    #     user_details = client.get_user(AccessToken=access_token)

    return UserResponse(**user_details)
