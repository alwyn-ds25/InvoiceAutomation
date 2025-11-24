# config/accounting_schemas.py

# This file defines the mappings from the canonical invoice schema to the
# schemas of various target accounting systems like Zoho and Tally.

ZOHO_MAPPING = {
    "customer_name": "vendor_name",
    "invoice_number": "invoice_number",
    "date": "invoice_date",
    "line_items": {
        "__source_list__": "line_items",
        "item_id": lambda item, index: f"item_{index+1}",
        "name": "description",
        "rate": "unit_price",
        "quantity": "quantity"
    },
    "total": "total_amount"
}

# This is a simplified representation. Tally often requires a specific XML format.
TALLY_MAPPING = {
    "VOUCHER": {
        "DATE": "invoice_date",
        "PARTYLEDGERNAME": "vendor_name",
        "ALLLEDGERENTRIES.LIST": {
            "__source_list__": "line_items",
            "LEDGERNAME": "description",
            "AMOUNT": "total"
        }
    }
}

# A generic function to transform data based on a mapping
def transform_to_target_schema(source_data, mapping):
    target_data = {}
    for target_key, source_key in mapping.items():
        if isinstance(source_key, dict):
            # Handle nested structures and list transformations
            list_key = source_key.pop("__source_list__", None)
            if list_key:
                target_data[target_key] = [
                    transform_to_target_schema(item, source_key)
                    for i, item in enumerate(source_data.get(list_key, []))
                ]
            else:
                target_data[target_key] = transform_to_target_schema(source_data, source_key)
        elif callable(source_key):
             # Handle lambda functions for dynamic field generation
            pass # Not fully implemented for this example
        else:
            if source_key in source_data:
                target_data[target_key] = source_data[source_key]
    return target_data
