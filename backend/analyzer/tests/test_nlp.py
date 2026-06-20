from django.test import TestCase
from analyzer.nlp import NLPProcessor

class NLPProcessorTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nlp_processor = NLPProcessor()

    def test_extract_contact_info(self):
        text = "Jane Doe\nEmail: jane.doe@example.com\nPhone: +1-555-555-0199\nSoftware Engineer"
        contact = self.nlp_processor.extract_contact_info(text)
        
        self.assertEqual(contact["email"], "jane.doe@example.com")
        self.assertEqual(contact["phone"], "+1-555-555-0199")
        # Name should be extracted (either Jane Doe via PERSON entity or first line fallback)
        self.assertTrue("Jane" in contact["name"] or contact["name"] == "Jane Doe")

    def test_extract_skills(self):
        text = "I have experience working with Python, React, Next.js and Docker."
        skills = self.nlp_processor.extract_skills(text)
        
        # Expected skills extracted should match original taxonomy spelling (which is lowercase)
        self.assertIn("python", skills)
        self.assertIn("react", skills)
        self.assertIn("next.js", skills)
        self.assertIn("docker", skills)

    def test_categorize_skills(self):
        matched_skills = ["python", "react", "docker"]
        categories = self.nlp_processor.categorize_skills(matched_skills)
        
        self.assertIn("Languages", categories)
        self.assertIn("python", categories["Languages"])
        self.assertIn("Frontend", categories)
        self.assertIn("react", categories["Frontend"])
        self.assertIn("Cloud & DevOps", categories)
        self.assertIn("docker", categories["Cloud & DevOps"])
