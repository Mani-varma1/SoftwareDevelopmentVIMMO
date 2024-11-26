import re

def panel_space_validator(panel_id_value, rcode_value, hgnc_id_value):
    # Define patterns for Panel_ID, Rcode, and HGNC_ID
    rcode_pattern = r"^R\d+$"      # Pattern for Rcode: Starts with 'R', followed by digits only
    panel_pattern = r"^\d+$"       # Pattern for Panel_ID: Matches only digits
    hgnc_pattern = r"^HGNC:\d+$"   # Pattern for HGNC_ID: Starts with 'HGNC:', followed by digits

    # Validate the format of Panel_ID - must be a number
    if panel_id_value:
        if not re.fullmatch(panel_pattern, str(panel_id_value)):  # Validate Panel_ID format
            raise ValueError("Invalid format for 'Panel_ID': Must be a number (e.g., '1234').")

    # Validate the format of Rcode - must start with 'R' and be followed by digits only
    if rcode_value:
        if not re.fullmatch(rcode_pattern, rcode_value):  # Validate Rcode format
            raise ValueError("Invalid format for 'Rcode': Must start with 'R' followed by digits only (e.g., 'R123').")

    # Validate the format of HGNC_ID - must start with 'HGNC:' and be followed by digits only
    if hgnc_id_value:
        if not re.fullmatch(hgnc_pattern, hgnc_id_value):  # Validate HGNC_ID format
            raise ValueError("Invalid format for 'HGNC_ID': It must start with 'HGNC:' followed by digits only (e.g., 'HGNC:12345').")
        



def bed_space_validator(panel_id_value, rcode_value, hgnc_id_value):
    pass





def validate_panel_id_or_Rcode_or_hgnc(args, panel_space=False, bed_space=False):
    """Custom validation for Panel_ID, Rcode, and HGNC_ID."""
    
    # Extract the values of Panel_ID, Rcode, and HGNC_ID from the input dictionary
    panel_id_value = args.get('Panel_ID', None)          # Panel ID
    rcode_value = args.get('Rcode', None)                # R-code
    hgnc_id_value = args.get('HGNC_ID', None)            # HGNC_ID

        # Ensure at least one argument is provided
    if not any([panel_id_value, rcode_value, hgnc_id_value]):
        raise ValueError("At least one of 'Panel_ID', 'Rcode', or 'HGNC_ID' must be provided.")

    # Ensure only one argument is provided
    if sum(bool(arg) for arg in [panel_id_value, rcode_value, hgnc_id_value]) > 1:
        raise ValueError("Provide only one of 'Panel_ID', 'Rcode', or 'HGNC_ID', not multiple.")
    

    if panel_space:
        panel_space_validator(panel_id_value, rcode_value, hgnc_id_value)

    if bed_space:
        bed_space_validator(panel_id_value, rcode_value, hgnc_id_value)