import os
import joblib

class JobRoleClassifier:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'job_role_classifier.joblib')
        self.vectorizer_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'skills_vectorizer.joblib')
        
        self.model = None
        self.vectorizer = None
        
        self.load_model()

    def load_model(self):
        """
        Loads the pre-trained ML model and TF-IDF vectorizer.
        """
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
            except Exception as e:
                print(f"Error loading classifier models: {str(e)}")

    def predict_role(self, skills):
        """
        Predicts job role probability based on list of skills.
        Returns a dict containing the primary predicted role and a detailed list of probabilities.
        """
        # If model is not loaded, do a rule-based fallback
        if self.model is None or self.vectorizer is None:
            return self._fallback_predict(skills)
            
        # Join skills into a single space-separated string
        skills_text = " ".join(skills)
        if not skills_text.strip():
            return {
                "primary_role": "Backend Developer",
                "probabilities": {
                    "Backend Developer": 25.0,
                    "Frontend Developer": 25.0,
                    "Android Developer": 25.0,
                    "ML Engineer": 25.0
                }
            }
            
        try:
            # Transform text
            features = self.vectorizer.transform([skills_text])
            probabilities = self.model.predict_proba(features)[0]
            classes = self.model.classes_
            
            # Map probabilities to classes
            prob_dict = {}
            for cls, prob in zip(classes, probabilities):
                prob_dict[cls] = round(float(prob) * 100, 2)
                
            primary_role = max(prob_dict, key=prob_dict.get)
            
            return {
                "primary_role": primary_role,
                "probabilities": prob_dict
            }
        except Exception as e:
            print(f"Prediction failed, falling back: {str(e)}")
            return self._fallback_predict(skills)

    def _fallback_predict(self, skills):
        """
        Rule-based classifier to use if machine learning models aren't ready yet.
        """
        skills_lower = [s.lower() for s in skills]
        
        scores = {
            "Backend Developer": 0,
            "Frontend Developer": 0,
            "Android Developer": 0,
            "ML Engineer": 0
        }
        
        # Simple keywords count
        backend_keys = ["django", "flask", "fastapi", "spring", "java", "node", "express", "sql", "postgres", "mysql", "mongodb", "docker", "aws", "gcp", "go", "golang", "microservices", "graphql"]
        frontend_keys = ["html", "css", "javascript", "typescript", "react", "vue", "angular", "next.js", "redux", "tailwind", "bootstrap", "sass", "webpack", "vite"]
        android_keys = ["kotlin", "android", "jetpack", "compose", "retrofit", "flutter", "dagger", "hilt", "firebase", "mobile"]
        ml_keys = ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy", "nlp", "spacy", "nltk", "opencv", "computer vision", "transformers", "llm", "langchain", "xgboost"]
        
        for skill in skills_lower:
            # Check substrings
            for key in backend_keys:
                if key in skill: scores["Backend Developer"] += 1
            for key in frontend_keys:
                if key in skill: scores["Frontend Developer"] += 1
            for key in android_keys:
                if key in skill: scores["Android Developer"] += 1
            for key in ml_keys:
                if key in skill: scores["ML Engineer"] += 1
                
        total = sum(scores.values())
        if total == 0:
            return {
                "primary_role": "Backend Developer",
                "probabilities": {
                    "Backend Developer": 25.0,
                    "Frontend Developer": 25.0,
                    "Android Developer": 25.0,
                    "ML Engineer": 25.0
                }
            }
            
        prob_dict = {}
        for role, score in scores.items():
            prob_dict[role] = round((score / total) * 100, 2)
            
        primary_role = max(prob_dict, key=prob_dict.get)
        
        return {
            "primary_role": primary_role,
            "probabilities": prob_dict
        }
