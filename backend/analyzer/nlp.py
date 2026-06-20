import re
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer
import numpy as np

# A comprehensive categorized database of technical skills
SKILLS_TAXONOMY = {
    "Languages": [
        "python", "javascript", "typescript", "java", "kotlin", "swift", "c++", "c", "c#", "go", "golang",
        "ruby", "php", "rust", "scala", "dart", "html", "css", "sql", "r", "shell", "bash"
    ],
    "Frontend": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte", "redux", "redux-toolkit",
        "tailwind", "tailwind css", "bootstrap", "sass", "webpack", "vite", "jquery", "html5", "css3", "less"
    ],
    "Backend": [
        "django", "flask", "fastapi", "spring boot", "spring", "node.js", "node", "express", "express.js",
        "laravel", "ruby on rails", "rails", "asp.net", "nest.js", "graphql", "rest api", "restful api",
        "microservices", "grpc", "celery"
    ],
    "Databases & Cache": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "cassandra", "elasticsearch",
        "dynamodb", "mariadb", "oracle", "firebase"
    ],
    "Cloud & DevOps": [
        "docker", "kubernetes", "k8s", "aws", "amazon web services", "gcp", "google cloud", "azure",
        "terraform", "ansible", "jenkins", "ci/cd", "github actions", "prometheus", "grafana"
    ],
    "Mobile": [
        "android", "ios", "react native", "flutter", "swiftui", "jetpack compose", "xcode", "android studio"
    ],
    "ML & Data Science": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras", "pandas",
        "numpy", "nlp", "natural language processing", "spacy", "nltk", "opencv", "computer vision",
        "transformers", "huggingface", "llm", "langchain", "xgboost", "random forest", "data analysis"
    ],
    "Tools & PM": [
        "git", "github", "gitlab", "jira", "confluence", "agile", "scrum", "trello", "docker", "postman"
    ]
}

# Flatten for matching
ALL_SKILLS = [skill for cat_skills in SKILLS_TAXONOMY.values() for skill in cat_skills]

class NLPProcessor:
    def __init__(self):
        # Load spaCy
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            # Fallback if not bootstrapped yet
            self.nlp = spacy.blank("en")
            
        # Build PhraseMatcher
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        # Add skill patterns
        patterns = [self.nlp.make_doc(skill) for skill in ALL_SKILLS]
        self.matcher.add("SKILLS", patterns)
        
        # Load Sentence Transformer lazily to save startup time
        self.embedding_model = None

    def _get_embedding_model(self):
        if self.embedding_model is None:
            # Using a fast, lightweight Sentence Transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def extract_contact_info(self, text):
        """
        Extracts name, email, and phone number from text.
        """
        email = None
        phone = None
        name = None
        
        # Email Regex
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        if email_match:
            email = email_match.group(0)
            
        # Phone Regex (supports multiple common formats)
        phone_match = re.search(r'(\+?\d{1,4}[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,9})', text)
        if phone_match:
            phone = phone_match.group(0)
            
        # Name Extraction (heuristic: first few lines of text, using spaCy PERSON entity)
        doc = self.nlp(text[:1000])  # Scan first 1000 chars for candidate name
        person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        if person_entities:
            # Return first valid person entity found near the top
            name = person_entities[0].strip()
        else:
            # Fallback to the first non-empty line
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                name = lines[0]
                
        # Clean name if it has multiline matches
        if name:
            name = name.split('\n')[0].strip()
                
        return {
            "name": name or "Unknown Candidate",
            "email": email or "Not Found",
            "phone": phone or "Not Found"
        }

    def extract_skills(self, text):
        """
        Matches resume text against skills taxonomy using spaCy PhraseMatcher.
        Returns a list of unique matched skills.
        """
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        matched_skills = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            # Normalize to the skill string as defined in taxonomy (for capitalization consistency)
            matched_skill_lower = span.text.lower()
            
            # Find the original representation from the taxonomy
            matched_skill_orig = matched_skill_lower
            for cat, skills in SKILLS_TAXONOMY.items():
                for s in skills:
                    if s.lower() == matched_skill_lower:
                        matched_skill_orig = s
                        break
            matched_skills.add(matched_skill_orig)
            
        # Return sorted list
        return sorted(list(matched_skills))

    def categorize_skills(self, matched_skills):
        """
        Groups the matched skills into categories.
        """
        categories = {}
        for cat, skills in SKILLS_TAXONOMY.items():
            cat_matched = [s for s in matched_skills if s.lower() in [sk.lower() for sk in skills]]
            if cat_matched:
                categories[cat] = cat_matched
        return categories

    def calculate_semantic_similarity(self, resume_text, jd_text):
        """
        Computes cosine similarity between resume text and job description using Sentence Transformers.
        """
        if not resume_text or not jd_text:
            return 0.0
            
        model = self._get_embedding_model()
        embeddings = model.encode([resume_text, jd_text])
        
        # Cosine similarity
        emb1, emb2 = embeddings[0], embeddings[1]
        dot_product = np.dot(emb1, emb2)
        norm_emb1 = np.linalg.norm(emb1)
        norm_emb2 = np.linalg.norm(emb2)
        
        if norm_emb1 == 0 or norm_emb2 == 0:
            return 0.0
            
        similarity = dot_product / (norm_emb1 * norm_emb2)
        # Convert from [-1, 1] to [0, 1] range
        similarity = float((similarity + 1) / 2)
        return round(similarity * 100, 2)
        
    def analyze_resume_vs_jd(self, resume_text, jd_text):
        """
        Full pipeline: Skill matching, missing skills, semantic similarity, and overall score.
        """
        # Extract contact and skills
        contact_info = self.extract_contact_info(resume_text)
        resume_skills = self.extract_skills(resume_text)
        
        # Extract skills from job description
        jd_skills = self.extract_skills(jd_text)
        
        # Identify matching and missing skills
        matching_skills = [s for s in jd_skills if s in resume_skills]
        missing_skills = [s for s in jd_skills if s not in resume_skills]
        
        # Calculate skills coverage ratio (percentage of JD skills covered)
        if len(jd_skills) > 0:
            skill_coverage = len(matching_skills) / len(jd_skills) * 100
        else:
            # If JD has no skills, default to a high fallback or 0
            skill_coverage = 100.0 if len(resume_skills) > 0 else 0.0
            
        # Semantic similarity
        semantic_score = self.calculate_semantic_similarity(resume_text, jd_text)
        
        # Combined score calculation: 40% skill coverage + 60% semantic similarity
        overall_score = (0.4 * skill_coverage) + (0.6 * semantic_score)
        overall_score = min(100.0, round(overall_score, 2))
        
        return {
            "contact_info": contact_info,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "skill_coverage": round(skill_coverage, 2),
            "semantic_score": semantic_score,
            "overall_score": overall_score,
            "categories": self.categorize_skills(resume_skills)
        }
