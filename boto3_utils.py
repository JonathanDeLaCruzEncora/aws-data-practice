import streamlit as st

def get_all_items(table):
    items = []
    last_evaluated_key = None

    while True:
        scan_params = {}
        if last_evaluated_key:
            scan_params["ExclusiveStartKey"] = last_evaluated_key

        response = table.scan(**scan_params)
        items.extend(response.get("Items", []))

        if "LastEvaluatedKey" not in response:
            break  # No more data to scan
        last_evaluated_key = response["LastEvaluatedKey"]

    return items


