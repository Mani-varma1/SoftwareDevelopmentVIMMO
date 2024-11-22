import unittest
from flask_restx import reqparse, inputs
from parser import IDParser

class TestParsers(unittest.TestCase):

    def test_id_parser_arguments(self):
        """Test IDParser to ensure it defines the expected arguments."""
        parser = IDParser.create_parser()
        args = parser.args  # This will give you the list of argument objects
        self.assertIn('Panel_ID', [arg.name for arg in args])
        self.assertIn('Rcode', [arg.name for arg in args])
        self.assertIn('HGNC_ID', [arg.name for arg in args])
        self.assertIn('Similar_Matches', [arg.name for arg in args])

    # def test_id_parser_custom_values(self):
    #     """Test IDParser with custom values."""
    #     parser = IDParser.create_parser()
    #     # Passing in a list of arguments as you would from a query string
    #     args = parser.parse_args(['Panel_ID', '123', 'Similar_Matches', 'true'])
    #     self.assertEqual(args['Panel_ID'], 123)
    #     self.assertEqual(args['Similar_Matches'], True)

    # def test_id_parser_default_values(self):
    #     """Test default values in IDParser."""
    #     parser = IDParser.create_parser()
    #     args = parser.parse_args([])  # No input arguments
    #     self.assertEqual(args['Panel_ID'], None)  # Default value is None
    #     self.assertEqual(args['Rcode'], None)
    #     self.assertEqual(args['HGNC_ID'], None)
    #     self.assertEqual(args['Similar_Matches'], False)  # Default value is False

if __name__ == '__main__':
    unittest.main()
