from typing import Any, Dict, List, Literal, TypeVar

import stripe

from api_lib import utils as U


def process_stripe_crud_event(
    event_data: Dict[str, Any],
    table: str,
    operation: Literal["created", "updated", "deleted"],
) -> Dict[str, Any]:
    client = U.get_client(service_name="dynamodb")
    deserialized_data = event_data["data"]["object"]
    serialized_data = U.type_serializer.serialize(deserialized_data)["M"]

    def create():
        return client.put_item(
            TableName=table,
            Item=serialized_data,
        )

    def update():
        described = client.describe_table(TableName=table)

        keys = [key["AttributeName"] for key in described["Table"]["KeySchema"]]

        key_items = {k: serialized_data[k] for k in keys}

        # create the set expression

        update_expression = "set "
        attribute_values = {}
        expression_attribute_names = {}

        counter = 0

        for k, v in serialized_data.items():
            if k not in key_items.keys():
                expression_attribute_name = f"#{k}"
                update_expression += f"{expression_attribute_name} = :a{counter}, "
                expression_attribute_names[expression_attribute_name] = k
                attribute_values[f":a{counter}"] = v
                counter += 1

        update_expression = update_expression.rstrip(", ")

        return client.update_item(
            TableName=table,
            Key=key_items,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
        )

    def delete() -> Dict[str, Any]:
        described = client.describe_table(TableName=table)

        schema = described["Table"]["KeySchema"]

        keys = [v["AttributeName"] for v in schema]

        items = client.query(
            TableName=table,
            KeyConditionExpression=f"{keys[0]} = :a0",
            ExpressionAttributeValues={":a0": serialized_data[keys[0]]},
        )["Items"]

        responses = []

        for item in items:
            responses.append(
                client.delete_item(TableName=table, Key={k: item[k] for k in keys})
            )
        return responses

    response = "Nothing"

    match operation:
        case "created":
            response = create()
        case "updated":
            response = update()
        case "deleted":
            response = delete()
    client.close()
    return response


def process_checkout_session_completed_event(event_data: Dict[str, Any]):
    checkout_table = (
        f"{U.COMPANY}-{U.DEVELOPMENT_ENVIRONMENT}-checkout-session-completed"
    )
    event_data["data"]["object"]["line_items"] = (
        stripe.checkout.Session.list_line_items(
            event_data["data"]["object"]["id"]
        )["data"]
    )
    if event_data["data"]["object"]["customer"] is None:
        event_data["data"]["object"]["customer"] = "N/A"
    return process_stripe_crud_event(
        event_data=event_data, table=checkout_table, operation="created"
    )


T = TypeVar("T")


def get_table_items(
    table_name: str,
    mode: T,
    active_only: bool = True,
) -> List[T]:
    client = U.get_client(service_name="dynamodb")

    if active_only:
        statement = f'select * from "{table_name}" where active=true'
    else:
        statement = f'select * from "{table_name}"'

    serialized_products = client.execute_statement(Statement=statement)["Items"]

    deserialized_products = [
        {k: U.type_deserializer.deserialize(v) for k, v in S.items()}
        for S in serialized_products
    ]

    return [mode(**p) for p in deserialized_products]
