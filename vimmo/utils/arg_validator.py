import re

def validate_id_or_hgnc(args):
    """Custom validation for ID and HGNC_ID."""
    id_value = args.get('ID', None)
    hgnc_id_value = args.get('HGNC_ID', None)

    # Define patterns for ID and HGNC_ID
    rcode_pattern = r"^R\d+(\.\d+)?$"  # Starts with 'R', followed by one or more digits, optionally a period and more digits
    panel_pattern=r"\d+"
    hgnc_pattern = r"^HGNC:\d+$"  # Starts with 'HGNC:', followed by one or more digits

    # Ensure at least one argument is provided
    if not id_value and not hgnc_id_value:
        raise ValueError("At least one of 'ID' or 'HGNC_ID' must be provided.")

    # Ensure only one argument is provided
    if id_value and hgnc_id_value:
        raise ValueError("Provide only one of 'ID' or 'HGNC_ID', not both.")

    # Validate the format of ID
    if id_value and not re.match(rcode_pattern, id_value) and id_value and not re.match(panel_pattern, id_value):
        raise ValueError(
            "Invalid format for 'ID':"
            "'R123' or 'R123.4' format for R codes  /  "
            "'123' format for Panel ID."
        )

    # Validate the format of HGNC_ID
    if hgnc_id_value and not re.match(hgnc_pattern, hgnc_id_value):
        raise ValueError(
            "Invalid format for 'HGNC_ID'. It must start with 'HGNC:', followed by one or more digits (e.g., 'HGNC:12345')."
        )
    
