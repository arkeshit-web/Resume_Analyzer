from django.test import TestCase
from analyzer.parser import clean_text

class ParserTestCase(TestCase):
    def test_clean_text_spaces(self):
        raw_text = "Hello    World!   \n   This is   a test.   "
        expected = "Hello World!\nThis is a test."
        self.assertEqual(clean_text(raw_text), expected)

    def test_clean_text_empty(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")
