from django.db import models

class ResumeAnalysis(models.Model):
    candidate_name = models.CharField(max_length=255, default="Unknown")
    candidate_email = models.CharField(max_length=255, default="Not Found")
    candidate_phone = models.CharField(max_length=100, default="Not Found")
    
    # Store skills as JSON lists
    resume_skills = models.JSONField(default=list)
    matching_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    skills_by_category = models.JSONField(default=dict)
    
    # Scores
    skill_coverage = models.FloatField(default=0.0)
    semantic_score = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    
    # ML Classifications
    predicted_role = models.CharField(max_length=100, default="Unknown")
    role_probabilities = models.JSONField(default=dict)
    
    # LLM Feedback
    ai_feedback = models.JSONField(default=dict)
    
    # Job Description & metadata
    job_description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate_name} - {self.predicted_role} ({self.overall_score}%)"
