import re

def validate_id_or_hgnc(args):
    """Custom validation for ID and HGNC_ID."""
    id_value = args.get('ID', None)
    hgnc_id_value = args.get('HGNC_ID', None)

    # Define patterns for ID and HGNC_ID
    rcode_pattern = r"^R\d+$"  # Starts with 'R', followed by digits only
    panel_pattern = r"^\d+$"  # Matches numbers (only digits)
    hgnc_pattern = r"^HGNC:\d+$"  # Starts with 'HGNC:', followed by digits

    # Ensure at least one argument is provided
    if not id_value and not hgnc_id_value:
        raise ValueError("At least one of 'ID' or 'HGNC_ID' must be provided.")

    # Ensure only one argument is provided
    if id_value and hgnc_id_value:
        raise ValueError("Provide only one of 'ID' or 'HGNC_ID', not both.")

    # Check if ID starts with a lowercase 'r'
    if id_value and id_value.startswith('r'):
        raise ValueError("Invalid format: 'ID' starts with a lowercase 'r'. It must start with an uppercase 'R'.")

    # Check if ID starts with a capital 'R' or is a number
    if id_value:
        if re.match(rcode_pattern, id_value):  # Valid R-code
            pass
        elif re.match(panel_pattern, id_value):  # Valid number
            pass
        else:
            raise ValueError(
                "Invalid format for 'ID': Must be either a number (e.g., '1234') "
                "or a code starting with an uppercase 'R' followed by digits only (e.g., 'R123')."
            )

    # Validate the format of HGNC_ID
    if hgnc_id_value and not re.match(hgnc_pattern, hgnc_id_value):
        raise ValueError(
            "Invalid format for 'HGNC_ID'. It must start with 'HGNC:', followed by one or more digits (e.g., 'HGNC:12345')."
        )
