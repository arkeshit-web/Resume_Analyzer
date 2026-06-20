import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

def setup_spacy():
    print("Checking spaCy NLP model...")
    try:
        import spacy
        if not spacy.util.is_package("en_core_web_sm"):
            print("spaCy model 'en_core_web_sm' not found. Downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            print("spaCy model downloaded successfully.")
        else:
            print("spaCy model 'en_core_web_sm' is already installed.")
    except ImportError:
        print("spaCy is not installed. Please run pip install first.")
        sys.exit(1)

def train_job_role_classifier():
    print("Training Job Role Classifier...")
    
    # Define skills per category to create synthetic training data
    role_skills = {
        "Backend Developer": [
            "Python Django Flask FastAPI Rest-API SQL PostgreSQL MySQL MongoDB Redis Docker AWS GraphQL Node.js Express Java Spring-Boot Go Golang Microservices Git Kubernetes",
            "Java Spring-Boot SQL PostgreSQL Hibernate Docker Microservices REST-API AWS Git Kubernetes JUnit",
            "Node.js Express JavaScript TypeScript MongoDB SQL PostgreSQL Redis Docker GraphQL REST-API AWS Git",
            "Python FastAPI SQL PostgreSQL Redis MongoDB Docker AWS Git REST-API gRPC Microservices",
            "Go Golang SQL PostgreSQL Redis Docker Kubernetes AWS Microservices gRPC REST-API Git",
            "Python Flask Django SQL MySQL Redis Docker Celery REST-API Git AWS Jenkins",
            "Ruby Rails SQL PostgreSQL Redis Sidekiq Docker AWS Git REST-API",
            "C# .NET Core ASP.NET SQL SQL-Server Azure Docker REST-API Microservices Git"
        ],
        "Frontend Developer": [
            "HTML CSS JavaScript TypeScript React Redux Tailwind Bootstrap Webpack SASS Git Next.js",
            "HTML CSS JavaScript TypeScript React Next.js Tailwind Webpack Git CSS-in-JS Responsive-Design",
            "HTML CSS JavaScript Vue Vuex Tailwind Bootstrap Git Vite Nuxt.js Webpack",
            "HTML CSS JavaScript Angular RxJS NGRX TypeScript Bootstrap Git Webpack Sass",
            "HTML CSS JavaScript TypeScript React Tailwind CSS Redux-Toolkit Vite Jest Git",
            "HTML CSS JavaScript TypeScript React Native Vue Tailwind Git Webpack SASS",
            "HTML CSS JavaScript jQuery Bootstrap SASS Responsive-Design Figma Git",
            "HTML CSS JavaScript React Next.js Vue Tailwind CSS UI/UX Webpack Git"
        ],
        "Android Developer": [
            "Kotlin Java Android-Studio SDK Jetpack-Compose Retrofit Dagger-Hilt Coroutines Firebase Git Gradle MVP MVVM",
            "Kotlin Android SDK Jetpack-Compose Coroutines Flow Retrofit Room Dagger-Hilt Git MVVM",
            "Java Android SDK Android-Studio XML SQLite Retrofit ButterKnife Firebase Git MVP MVC",
            "Kotlin Flutter Dart Android iOS Firebase Cross-Platform Git State-Management Bloc Provider",
            "Kotlin Android SDK Jetpack-Compose Room Retrofit Coroutines Dagger-Hilt Firebase Git MVVM Unit-Testing",
            "Java Kotlin Android-Studio SDK Jetpack Compose Retrofit Firebase Room Git MVVM Gradle",
            "Kotlin Android Studio Jetpack Compose Firebase Coroutines Retrofit Git MVVM",
            "Kotlin Android SDK Gradle Jetpack Compose Dagger Hilt Room Retrofit Firebase Git MVVM"
        ],
        "ML Engineer": [
            "Python Machine-Learning Deep-Learning TensorFlow PyTorch Scikit-Learn Pandas NumPy NLP spaCy Keras Transformers LLM Git",
            "Python Pandas NumPy Scikit-Learn Machine-Learning Matplotlib Seaborn SQL Git Statistics",
            "Python PyTorch Deep-Learning Computer-Vision OpenCV CNN Image-Processing TensorFlow Git",
            "Python NLP spaCy NLTK Transformers LLM HuggingFace Deep-Learning Text-Processing Git",
            "Python Machine-Learning Scikit-Learn TensorFlow PyTorch Keras LLM LangChain OpenAI Gemini Git XGBoost",
            "Python Machine-Learning Deep-Learning Pandas NumPy Scikit-Learn Matplotlib SQL Keras PyTorch Git",
            "Python Data-Science R SQL Pandas NumPy Scikit-Learn Machine-Learning Data-Visualization Statistics Git",
            "Python Deep-Learning TensorFlow PyTorch CNN RNN Transformers NLP Computer-Vision Git MLops"
        ]
    }
    
    # Generate synthetic training samples
    data = []
    np.random.seed(42)
    
    # We generate 100 samples for each class
    for role, templates in role_skills.items():
        for _ in range(100):
            # Pick a template and randomize skills slightly
            template = np.random.choice(templates)
            skills = template.split()
            # Randomly drop some skills, and add some common skills (like Git, SQL, Agile)
            keep_count = int(len(skills) * np.random.uniform(0.7, 1.0))
            chosen_skills = list(np.random.choice(skills, keep_count, replace=False))
            
            # 20% chance to add some generic tools
            if np.random.rand() < 0.3:
                chosen_skills.append("Git")
            if np.random.rand() < 0.2:
                chosen_skills.append("SQL")
            if np.random.rand() < 0.15:
                chosen_skills.append("Agile")
                
            skill_string = " ".join(chosen_skills)
            data.append({"skills": skill_string, "role": role})
            
    df = pd.DataFrame(data)
    
    # Vectorize the skills text
    vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'(?u)\b\w+\b')
    X = vectorizer.fit_transform(df["skills"])
    y = df["role"]
    
    # Train the Random Forest Classifier
    classifier = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    classifier.fit(X, y)
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    # Save model and vectorizer
    joblib.dump(classifier, "models/job_role_classifier.joblib")
    joblib.dump(vectorizer, "models/skills_vectorizer.joblib")
    print("Job Role Classifier trained and saved successfully in 'models/'.")

if __name__ == "__main__":
    setup_spacy()
    train_job_role_classifier()
    print("Bootstrap completed successfully!")
