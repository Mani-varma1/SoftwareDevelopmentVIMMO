import unittest
from arg_validator import validate_panel_id_or_Rcode_or_hgnc  # Import the function to test


class TestValidateIDOrRcodeOrHGNC(unittest.TestCase):
    """Unit tests for the validate_panel_id_or_Rcode_or_hgnc function."""

    def test_valid_panel_id(self):
        """Test valid Panel_ID."""
        args = {"Panel_ID": "1234"}  # Valid input: Panel_ID as a number
        try:
            validate_panel_id_or_Rcode_or_hgnc(args)
        except ValueError as e:
            self.fail(f"Function raised ValueError unexpectedly: {e}")

    def test_invalid_panel_id(self):
        """Test invalid Panel_ID format."""
        args = {"Panel_ID": "12a34"}  # Invalid: contains non-numeric characters
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        # Ensure the error message mentions the invalid Panel_ID format
        self.assertIn("Invalid format for 'Panel_ID': Must be a number", str(context.exception))

    def test_valid_rcode(self):
        """Test valid Rcode."""
        args = {"Rcode": "R123"}  # Valid Rcode
        try:
            validate_panel_id_or_Rcode_or_hgnc(args)
        except ValueError as e:
            self.fail(f"Function raised ValueError unexpectedly: {e}")

    def test_invalid_rcode(self):
        """Test invalid Rcode format."""
        args = {"Rcode": "r123"}  # Invalid: starts with lowercase "r"
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        self.assertIn("Invalid format for 'Rcode': Must start with 'R' followed by digits only", str(context.exception))

    def test_valid_hgnc_id(self):
        """Test valid HGNC_ID."""
        args = {"HGNC_ID": "HGNC:12345"}  # Valid HGNC_ID
        try:
            validate_panel_id_or_Rcode_or_hgnc(args)
        except ValueError as e:
            self.fail(f"Function raised ValueError unexpectedly: {e}")

    def test_invalid_hgnc_id_missing_colon(self):
        """Test invalid HGNC_ID missing colon."""
        args = {"HGNC_ID": "HGNC12345"}  # Invalid: missing colon
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        self.assertIn("Invalid format for 'HGNC_ID'", str(context.exception))

    def test_invalid_hgnc_id_lowercase(self):
        """Test invalid lowercase HGNC_ID."""
        args = {"HGNC_ID": "hgnc:12345"}  # Invalid: starts with lowercase "hgnc"
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        self.assertIn("Invalid format for 'HGNC_ID'", str(context.exception))

    def test_no_input_provided(self):
        """Test when no input is provided."""
        args = {}  # No input provided
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        self.assertIn("At least one of 'Panel_ID', 'Rcode', or 'HGNC_ID' must be provided", str(context.exception))

    def test_multiple_inputs_provided(self):
        """Test when multiple inputs are provided."""
        args = {"Panel_ID": "1234", "Rcode": "R123"}  # Multiple inputs provided
        with self.assertRaises(ValueError) as context:
            validate_panel_id_or_Rcode_or_hgnc(args)
        self.assertIn("Provide only one of 'Panel_ID', 'Rcode', or 'HGNC_ID'", str(context.exception))


if __name__ == "__main__":
    unittest.main()
