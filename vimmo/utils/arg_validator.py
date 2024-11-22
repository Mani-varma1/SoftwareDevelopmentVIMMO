import re

def validate_id_or_hgnc(args):
    """Custom validation for Panel_ID, Rcode, and HGNC_ID."""
    panel_id_value = args.get('Panel_ID', None)          # Panel ID
    rcode_value = args.get('Rcode', None)                # R-code
    hgnc_id_value = args.get('HGNC_ID', None)            # HGNC_ID

    # Define patterns for Panel_ID, Rcode, and HGNC_ID
    rcode_pattern = r"^R\d+$"      # Starts with 'R', followed by digits only
    panel_pattern = r"^\d+$"       # Matches only digits (for Panel_ID)
    hgnc_pattern = r"^HGNC:\d+$"  # Starts with 'HGNC:', followed by digits

    # Ensure at least one argument is provided
    if not any([panel_id_value, rcode_value, hgnc_id_value]):
        raise ValueError("At least one of 'Panel_ID', 'Rcode', or 'HGNC_ID' must be provided.")

    # Ensure only one argument is provided
    if sum(bool(arg) for arg in [panel_id_value, rcode_value, hgnc_id_value]) > 1:
        raise ValueError("Provide only one of 'Panel_ID', 'Rcode', or 'HGNC_ID', not multiple.")

    # Validate the format of Panel_ID - only numbers
    if panel_id_value:
        if not re.fullmatch(panel_pattern, str(panel_id_value)):  # Validate Panel_ID format
            raise ValueError("Invalid format for 'Panel_ID': Must be a number (e.g., '1234').")

    # Validate the format of Rcode - must start with 'R' and be followed by digits only
    if rcode_value:
        if not re.fullmatch(rcode_pattern, rcode_value):  # Validate Rcode format
            raise ValueError("Invalid format for 'Rcode': Must start with 'R' followed by digits only (e.g., 'R123').")

    # Validate the format of HGNC_ID
    if hgnc_id_value:
        if not re.fullmatch(hgnc_pattern, hgnc_id_value):
            raise ValueError("Invalid format for 'HGNC_ID': It must start with 'HGNC:' followed by digits only (e.g., 'HGNC:12345').")

