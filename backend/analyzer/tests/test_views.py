import json
from unittest.mock import patch
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from analyzer.models import ResumeAnalysis

class ViewsTestCase(APITestCase):
    def test_improve_project_endpoint(self):
        url = reverse('improve-project')
        data = {
            "weak_statement": "wrote python code",
            "target_role": "Backend Developer"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("improved_statement", response.data)
        self.assertEqual(response.data["original_statement"], "wrote python code")

    def test_leetcode_endpoint(self):
        url = reverse('leetcode') + "?username=testuser"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertIn("solved_all", response.data)
        self.assertIn("suggestions", response.data)

    def test_history_list_clear_endpoints(self):
        # Create a dummy analysis record
        ResumeAnalysis.objects.create(
            candidate_name="Alice",
            candidate_email="alice@example.com",
            resume_skills=["Python", "SQL"],
            matching_skills=["Python"],
            missing_skills=["SQL"],
            overall_score=75.0,
            predicted_role="Backend Developer"
        )
        
        # Test List
        url = reverse('history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["candidate_name"], "Alice")
        
        # Test Delete All
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResumeAnalysis.objects.count(), 0)

    @patch('analyzer.views.extract_text_from_pdf')
    def test_analyze_resume_endpoint(self, mock_extract):
        # Mock pdf extraction output
        mock_extract.return_value = "Jane Doe\nEmail: jane@example.com\nSkills: Python, Django, React"
        
        url = reverse('analyze')
        dummy_pdf = SimpleUploadedFile("resume.pdf", b"pdf_data", content_type="application/pdf")
        
        data = {
            "resume": dummy_pdf,
            "job_description": "We are looking for a Backend Developer with Python and Django skills."
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["candidate_name"], "Jane Doe")
        self.assertEqual(response.data["candidate_email"], "jane@example.com")
        self.assertIn("python", response.data["resume_skills"])
        self.assertIn(response.data["predicted_role"], ["Backend Developer", "ML Engineer", "Frontend Developer", "Android Developer"])
        self.assertGreater(response.data["overall_score"], 0)
