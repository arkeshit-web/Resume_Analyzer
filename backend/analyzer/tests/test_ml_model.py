from django.test import TestCase
from analyzer.ml_model import JobRoleClassifier

class MLModelTestCase(TestCase):
    def test_predict_role_fallback_backend(self):
        classifier = JobRoleClassifier()
        # Force fallback behavior or test direct predict
        skills = ["Django", "PostgreSQL", "Flask", "Docker"]
        prediction = classifier.predict_role(skills)
        
        self.assertIn("primary_role", prediction)
        self.assertIn("probabilities", prediction)
        self.assertEqual(prediction["primary_role"], "Backend Developer")
        self.assertGreater(prediction["probabilities"]["Backend Developer"], 0)

    def test_predict_role_fallback_frontend(self):
        classifier = JobRoleClassifier()
        skills = ["HTML", "CSS", "React", "Tailwind", "TypeScript"]
        prediction = classifier.predict_role(skills)
        
        self.assertEqual(prediction["primary_role"], "Frontend Developer")
