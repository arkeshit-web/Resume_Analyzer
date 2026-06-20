from django.apps import AppConfig
import sys

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'
    
    # Singletons for memory caching
    nlp_processor = None
    role_classifier = None
    feedback_generator = None

    def ready(self):
        # Prevent double loading in dev server reload
        if 'runserver' in sys.argv:
            # We defer actual heavy loading to avoid blocking dev server start-up checks
            # but we can load them or let them load lazily
            pass
            
        # Import lazily to avoid import cycles
        from .nlp import NLPProcessor
        from .ml_model import JobRoleClassifier
        from .ai_feedback import AIFeedbackGenerator
        
        # Instantiate singletons
        AnalyzerConfig.nlp_processor = NLPProcessor()
        AnalyzerConfig.role_classifier = JobRoleClassifier()
        AnalyzerConfig.feedback_generator = AIFeedbackGenerator()
        print("NLP, ML and AI modules loaded into memory cache.")
