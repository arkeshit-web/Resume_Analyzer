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

## 🌐 Deployed Endpoints
*   **Frontend**: Hosted on **Vercel**
*   **Backend API**: Hosted on **Hugging Face Spaces** (Docker SDK)
