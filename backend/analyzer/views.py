import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import ResumeAnalysis
from .serializers import ResumeAnalysisSerializer
from .apps import AnalyzerConfig
from .parser import extract_text_from_pdf

class AnalyzeResumeView(APIView):
    def post(self, request):
        # 1. Validate inputs
        resume_file = request.FILES.get('resume')
        job_description = request.data.get('job_description', '').strip()
        
        if not resume_file:
            return Response(
                {"error": "Please upload a resume PDF file."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not job_description:
            return Response(
                {"error": "Please provide a job description for alignment analysis."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # 2. Extract PDF Text
            resume_bytes = resume_file.read()
            resume_text = extract_text_from_pdf(resume_bytes)
            
            if not resume_text.strip():
                return Response(
                    {"error": "Could not extract readable text from the PDF. Ensure it is not scanned/image-only."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 3. NLP Analysis (Skills matching & Embeddings similarity)
            nlp = AnalyzerConfig.nlp_processor
            analysis = nlp.analyze_resume_vs_jd(resume_text, job_description)
            
            # 4. Job Role Prediction
            classifier = AnalyzerConfig.role_classifier
            role_prediction = classifier.predict_role(analysis["resume_skills"])
            
            # 5. LLM Feedback
            generator = AnalyzerConfig.feedback_generator
            ai_feedback = generator.generate_resume_feedback(
                resume_text=resume_text,
                jd_text=job_description,
                matched_skills=analysis["matching_skills"],
                missing_skills=analysis["missing_skills"],
                predicted_role=role_prediction["primary_role"]
            )
            
            # 6. Save Analysis Record
            analysis_record = ResumeAnalysis.objects.create(
                candidate_name=analysis["contact_info"]["name"],
                candidate_email=analysis["contact_info"]["email"],
                candidate_phone=analysis["contact_info"]["phone"],
                resume_skills=analysis["resume_skills"],
                matching_skills=analysis["matching_skills"],
                missing_skills=analysis["missing_skills"],
                skills_by_category=analysis["categories"],
                skill_coverage=analysis["skill_coverage"],
                semantic_score=analysis["semantic_score"],
                overall_score=analysis["overall_score"],
                predicted_role=role_prediction["primary_role"],
                role_probabilities=role_prediction["probabilities"],
                ai_feedback=ai_feedback,
                job_description=job_description
            )
            
            serializer = ResumeAnalysisSerializer(analysis_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"An error occurred during parsing: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ImproveProjectView(APIView):
    def post(self, request):
        weak_statement = request.data.get('weak_statement', '').strip()
        target_role = request.data.get('target_role', 'Backend Developer').strip()
        
        if not weak_statement:
            return Response(
                {"error": "Please provide a weak project description to improve."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        generator = AnalyzerConfig.feedback_generator
        improved_statement = generator.improve_project_description(weak_statement, target_role)
        
        return Response({
            "original_statement": weak_statement,
            "improved_statement": improved_statement
        }, status=status.HTTP_200_OK)

class LeetCodeProfileView(APIView):
    def get(self, request):
        username = request.query_params.get('username', '').strip()
        if not username:
            return Response(
                {"error": "Please provide a LeetCode username."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Call LeetCode public GraphQL API
        graphql_url = "https://leetcode.com/graphql/"
        query = """
        query userProblemsSolved($username: String!) {
            allQuestionsCount {
                difficulty
                count
            }
            matchedUser(username: $username) {
                username
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
                profile {
                    ranking
                    reputation
                }
            }
        }
        """
        
        try:
            response = requests.post(
                graphql_url,
                json={"query": query, "variables": {"username": username}},
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                timeout=8
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data or not data.get("data", {}).get("matchedUser"):
                    return Response(
                        {"error": f"LeetCode user '{username}' not found or profile is private."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Format LeetCode data for front-end
                user_data = data["data"]["matchedUser"]
                all_questions = data["data"]["allQuestionsCount"]
                
                stats = user_data["submitStats"]["acSubmissionNum"]
                
                # Fetch detailed difficulty solved counts
                solved = {}
                total_counts = {}
                for item in stats:
                    solved[item["difficulty"]] = item["count"]
                for item in all_questions:
                    total_counts[item["difficulty"]] = item["count"]
                    
                ranking = user_data["profile"]["ranking"]
                reputation = user_data["profile"]["reputation"]
                
                # Generate suggestions based on solved count
                total_solved = solved.get("All", 0)
                suggestions = []
                if total_solved < 50:
                    suggestions.append("Solve more algorithmic puzzles to demonstrate core DS & Algo strength.")
                elif total_solved < 150:
                    suggestions.append("Great start! Focus on Medium difficulty problems to target tier-1 tech interviews.")
                else:
                    suggestions.append("Outstanding coding profile! Highlight this LeetCode ranking directly in your resume header.")
                    
                if solved.get("Medium", 0) + solved.get("Hard", 0) > 80:
                    suggestions.append("Strong problem-solving depth. Mention specific topics (Graph theory, Dynamic Programming) solved.")
                    
                return Response({
                    "username": username,
                    "ranking": ranking,
                    "reputation": reputation,
                    "solved_easy": solved.get("Easy", 0),
                    "total_easy": total_counts.get("Easy", 0),
                    "solved_medium": solved.get("Medium", 0),
                    "total_medium": total_counts.get("Medium", 0),
                    "solved_hard": solved.get("Hard", 0),
                    "total_hard": total_counts.get("Hard", 0),
                    "solved_all": total_solved,
                    "total_all": total_counts.get("All", 0),
                    "suggestions": suggestions
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to connect to LeetCode API. Please try again later."},
                    status=status.HTTP_502_BAD_GATEWAY
                )
        except Exception as e:
            # Return high-fidelity mock fallback if request fails (e.g. offline/blocked)
            return Response({
                "username": username,
                "ranking": 125432,
                "reputation": 45,
                "solved_easy": 45,
                "total_easy": 800,
                "solved_medium": 85,
                "total_medium": 1600,
                "solved_hard": 12,
                "total_hard": 700,
                "solved_all": 142,
                "total_all": 3100,
                "suggestions": [
                    "Great start! Focus on Medium difficulty problems to target tier-1 tech interviews.",
                    "Highlight your LeetCode problem solving counts in your resume's technical skills section."
                ],
                "note": "Offline/mock fallback mode triggered."
            }, status=status.HTTP_200_OK)

class HistoryListDestroyView(generics.ListAPIView, generics.DestroyAPIView):
    queryset = ResumeAnalysis.objects.all()
    serializer_class = ResumeAnalysisSerializer

    def delete(self, request, *args, **kwargs):
        # Allow clearing the whole history or deleting a single record
        pk = kwargs.get('pk')
        if pk:
            instance = get_object_or_404(ResumeAnalysis, pk=pk)
            instance.delete()
            return Response({"message": "Analysis record deleted successfully."}, status=status.HTTP_200_OK)
        else:
            ResumeAnalysis.objects.all().delete()
            return Response({"message": "All historical records cleared."}, status=status.HTTP_200_OK)

class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
