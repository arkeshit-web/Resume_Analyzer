---
title: Resume Analyzer
emoji: 📄
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# ATSAlign | AI-Powered Resume Analyzer

ATSAlign is a premium, high-fidelity AI Resume Analyzer and ATS Alignment Checker. It evaluates resume PDF alignment against job descriptions, identifies formatting flaws, optimizes project descriptions using the STAR methodology, and predicts engineering tracks.

---

## 🚀 System Architecture

*   **Frontend**: A responsive Single-Page Dashboard built with HTML, Vanilla CSS (Glassmorphism), and Javascript.
*   **Backend**: Django REST Framework API backed by NLP (spaCy & Sentence Transformers) and Machine Learning (Scikit-Learn Random Forest Classifier).
*   **AI Engine**: Google Gemini API (`gemini-1.5-flash`) for structural analysis and STAR achievement optimization.

---

## 🛠️ Local Development

### 1. Run the Backend API
1.  Navigate into `backend/`.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate   # On Windows
    source .venv/bin/activate # On Unix/macOS
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the bootstrap script to download models and train the classifier:
    ```bash
    python bootstrap.py
    ```
5.  Start the development server:
    ```bash
    python manage.py runserver 127.0.0.1:8000
    ```

### 2. Run the Frontend
1.  Serve the `frontend/` directory (e.g., using Python's static server):
    ```bash
    python -m http.server 3000 --directory frontend
    ```
2.  Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🌐 Deployed Endpoints
*   **Frontend**: Hosted on **Vercel**
*   **Backend API**: Hosted on **Hugging Face Spaces** (Docker SDK)
