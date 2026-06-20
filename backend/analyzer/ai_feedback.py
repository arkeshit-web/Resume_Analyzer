import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure GenAI
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    HAS_GEMINI_KEY = True
else:
    HAS_GEMINI_KEY = False

class AIFeedbackGenerator:
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
        
    def generate_resume_feedback(self, resume_text, jd_text, matched_skills, missing_skills, predicted_role):
        """
        Uses Gemini to generate detailed resume analysis and improvement suggestions.
        """
        if not HAS_GEMINI_KEY:
            return self._generate_mock_feedback(matched_skills, missing_skills, predicted_role)
            
        prompt = f"""
        You are an expert HR Manager and Technical Recruiter. Analyze the candidate's resume text against the Job Description.
        
        Candidate's Predicted Role: {predicted_role}
        Extracted Matching Skills: {', '.join(matched_skills)}
        Extracted Missing Skills: {', '.join(missing_skills)}
        
        RESUME TEXT:
        \"\"\"{resume_text[:4000]}\"\"\"
        
        JOB DESCRIPTION:
        \"\"\"{jd_text[:4000]}\"\"\"
        
        Provide a detailed analysis in JSON format with the following keys. Do NOT include markdown code blocks or any text outside the JSON. Return valid JSON only.
        
        JSON Structure:
        {{
            "ats_issues": [
                "Issue 1 with severity (High/Medium/Low) and description",
                "Issue 2..."
            ],
            "weak_bullets": [
                {{
                    "original": "Original weak statement from the resume",
                    "reason": "Why it's weak (e.g., lack of metrics, passive tone)",
                    "improved": "Rewritten statement using the STAR method with numbers/metrics"
                }}
            ],
            "missing_skills_analysis": [
                {{
                    "skill": "Name of missing skill",
                    "importance": "High/Medium/Low",
                    "rationale": "Why this skill is critical for this job"
                }}
            ],
            "project_improvements": [
                {{
                    "current_project_context": "What project the resume mentions",
                    "suggestion": "How to enhance this project description or what feature to add to make it stand out"
                }}
            ],
            "action_plan": [
                "Step-by-step recommendation 1",
                "Step-by-step recommendation 2"
            ]
        }}
        """
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            # Clean up the output in case it contains markdown formatting
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            feedback_data = json.loads(text)
            return feedback_data
        except Exception as e:
            print(f"Gemini API error: {str(e)}. Falling back to mock generator.")
            return self._generate_mock_feedback(matched_skills, missing_skills, predicted_role)

    def improve_project_description(self, weak_statement, target_role):
        """
        Rewrites a weak bullet point into a STAR-method, metric-driven statement.
        """
        if not HAS_GEMINI_KEY:
            return self._generate_mock_bullet_improvement(weak_statement, target_role)
            
        prompt = f"""
        You are an elite career coach. Rewrite the following weak project description/bullet point into a professional, achievement-oriented, impact-focused statement for a {target_role} role. Use the STAR (Situation, Task, Action, Result) methodology. Incorporate realistic metrics, percentages, or numbers where appropriate. Keep it concise (1-2 sentences).
        
        Weak Statement: "{weak_statement}"
        
        Return ONLY the improved statement as plain text. Do not include introductory or concluding remarks.
        """
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error in project improver: {str(e)}")
            return self._generate_mock_bullet_improvement(weak_statement, target_role)

    def _generate_mock_feedback(self, matched_skills, missing_skills, predicted_role):
        """
        Generates structured, realistic mock feedback if the Gemini API is unavailable.
        """
        missing_skills_analysis = []
        for i, skill in enumerate(missing_skills[:4]):
            importance = "High" if i < 2 else "Medium"
            missing_skills_analysis.append({
                "skill": skill,
                "importance": importance,
                "rationale": f"Essential for core engineering requirements in modern {predicted_role} frameworks. Crucial for developer velocity and architectural efficiency."
            })
            
        # Standard fallback if missing skills is empty
        if not missing_skills_analysis:
            missing_skills_analysis.append({
                "skill": "System Design",
                "importance": "High",
                "rationale": "Large-scale systems engineering is critical to deploy robust components for a modern product workflow."
            })

        return {
            "ats_issues": [
                "High Severity: Resume length should ideally be 1 page for junior to mid-level roles. Condense bullet points.",
                "Medium Severity: Lack of measurable metrics (e.g., percentages, scale, throughput) in project descriptions.",
                "Low Severity: Ensure contact links (GitHub, LinkedIn) are clickable hyperlinked text."
            ],
            "weak_bullets": [
                {
                    "original": "Worked on backend endpoints and fixed database bugs.",
                    "reason": "Uses passive verbs and lacks concrete impact or technical scope.",
                    "improved": f"Designed and optimized 12+ REST endpoints using {matched_skills[0] if matched_skills else 'Python/Node'}, reducing API response latency by 24% and resolving critical database concurrency issues."
                },
                {
                    "original": "Responsible for creating React components for a dashboard.",
                    "reason": "Does not explain the complexity or the design principles applied.",
                    "improved": "Refactored legacy dashboard panels into reusable React hooks and components with state caching, improving render efficiency by 40% and enhancing user experience."
                }
            ],
            "missing_skills_analysis": missing_skills_analysis,
            "project_improvements": [
                {
                    "current_project_context": "Web Application Project",
                    "suggestion": f"Integrate containerization with Docker and add a monitoring endpoint. Document this setup to demonstrate clean devops principles."
                },
                {
                    "current_project_context": "Data Pipeline / Database integrations",
                    "suggestion": f"Introduce automated integration testing (e.g. PyTest/Jest) and configure a local Redis caching layer to demonstrate performance-first engineering."
                }
            ],
            "action_plan": [
                f"Integrate these missing core technologies: {', '.join(missing_skills[:3]) or 'Cloud Deployments'} into a side project.",
                "Rewrite your project bullet points to lead with strong action verbs (e.g., 'Architected', 'Spearheaded', 'Optimized') followed by the business result.",
                "Update your LeetCode profile to showcase active problem-solving skills, and links on your header.",
                "Re-upload your resume here to verify if the ATS score crosses the 85% threshold."
            ]
        }

    def _generate_mock_bullet_improvement(self, weak_statement, target_role):
        """
        Heuristic mock bullet improver.
        """
        # Analyze words in weak statement to make it look contextual
        weak_lower = weak_statement.lower()
        if "website" in weak_lower or "react" in weak_lower or "frontend" in weak_lower or "ui" in weak_lower:
            return f"Designed and built a responsive UI portal using React and CSS, increasing user engagement by 22% and improving page loading speeds by 30% through code-splitting and asset optimization."
        elif "backend" in weak_lower or "api" in weak_lower or "database" in weak_lower or "server" in weak_lower:
            return f"Architected a scalable RESTful API handling 10k+ daily active requests, implementing Redis caching and PostgreSQL query optimizations to cut system response times by 35%."
        elif "model" in weak_lower or "ml" in weak_lower or "data" in weak_lower or "predict" in weak_lower:
            return f"Developed and deployed a Random Forest classification model with 92% accuracy, optimizing hyper-parameters and feature engineering pipelines to reduce pipeline latency by 45%."
        else:
            # General fallback
            return f"Spearheaded the development and optimization of core product features, improving system performance by 25% and reducing developer setup time by automated scripting workflows."
        
