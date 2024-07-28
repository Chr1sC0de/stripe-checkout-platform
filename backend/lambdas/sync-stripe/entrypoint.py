from sync_stripe import utils


def handler(event, context):
    main()
    return {"message": "completed successfully"}


def main():
    utils.sync_completed_checkout_sessions()
    utils.sync_product_price_customer_table()


if __name__ == "__main__":
    handler((), {})
