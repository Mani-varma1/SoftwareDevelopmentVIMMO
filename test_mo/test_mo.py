import unittest
from mo_validate import validate_id_or_hgnc 

class TestValidateIDOrHGNC(unittest.TestCase):
    def test_valid_id(self):
        """Test valid ID inputs."""
        args = {"ID": "R123"}
        try:
            validate_id_or_hgnc(args)
        except ValueError:
            self.fail("validate_id_or_hgnc() raised ValueError unexpectedly for valid ID.")

        args = {"ID": "123"}
        try:
            validate_id_or_hgnc(args)
        except ValueError:
            self.fail("validate_id_or_hgnc() raised ValueError unexpectedly for valid numeric ID.")

    def test_valid_hgnc_id(self):
        """Test valid HGNC_ID inputs."""
        args = {"HGNC_ID": "HGNC:1234"}
        try:
            validate_id_or_hgnc(args)
        except ValueError:
            self.fail("validate_id_or_hgnc() raised ValueError unexpectedly for valid HGNC_ID.")

    def test_invalid_lowercase_r(self):
        """Test invalid lowercase 'r' in ID."""
        args = {"ID": "r123"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("starts with a lowercase 'r'", str(context.exception))

    def test_invalid_hgnc_lowercase(self):
        """Test invalid lowercase HGNC."""
        args = {"HGNC_ID": "hgnc:1234"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("It is lowercase. Use uppercase 'HGNC:'", str(context.exception))

    def test_invalid_hgnc_missing_colon(self):
        """Test HGNC_ID missing colon."""
        args = {"HGNC_ID": "HGNC1234"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("Missing colon ':'", str(context.exception))

    def test_invalid_hgnc_format(self):
        """Test invalid HGNC_ID format."""
        args = {"HGNC_ID": "HGNC:12,34"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("Must be 'HGNC:' followed by digits only", str(context.exception))

    def test_invalid_id_format(self):
        """Test invalid ID format."""
        args = {"ID": "ABC123"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("Must be either a number", str(context.exception))

    def test_missing_both_arguments(self):
        """Test when neither ID nor HGNC_ID is provided."""
        args = {}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("At least one of 'ID' or 'HGNC_ID' must be provided", str(context.exception))

    def test_both_arguments_provided(self):
        """Test when both ID and HGNC_ID are provided."""
        args = {"ID": "R123", "HGNC_ID": "HGNC:1234"}
        with self.assertRaises(ValueError) as context:
            validate_id_or_hgnc(args)
        self.assertIn("Provide only one of 'ID' or 'HGNC_ID'", str(context.exception))

# if __name__ == "__main__":
#     unittest.main()
