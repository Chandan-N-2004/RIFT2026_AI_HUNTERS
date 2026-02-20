# 🚑 PharmaGuard – Pharmacogenomic Risk Prediction System
## 📌 Overview

PharmaGuard is an AI-powered pharmacogenomic risk prediction platform designed to analyze patient genetic data and predict personalized drug response risks.

The system helps identify adverse drug reactions, optimize dosage recommendations, and provide explainable clinical insights using AI and genomic data.

This project was developed as part of the HealthTech AI Hackathon focusing on precision medicine and pharmacogenomics. 

PS3_PharmaGuard_HealthTech
---
## 🎯 Problem Statement

Adverse drug reactions cause significant mortality worldwide. Many of these cases can be prevented through pharmacogenomic testing that analyzes how genetic variations influence drug metabolism.

PharmaGuard addresses this by:

* Analyzing genomic VCF data

* Predicting drug safety and efficacy

* Providing AI-generated clinical explanations

* Supporting personalized treatment decisions

## 🚀 Key Features
### ✅ Genetic Data Processing

* VCF file parsing (Variant Call Format)

* Pharmacogene identification (CYP2D6, CYP2C19, CYP2C9, etc.)

### ✅ AI Risk Prediction

Drug risk classification:

* Safe

* Adjust Dosage

* Toxic

* Ineffective


### ✅ Explainable AI

* LLM-generated clinical explanations

* Variant-based risk reasoning

### ✅ Clinical Recommendations

* Personalized dosage suggestions

* CPIC guideline alignment

### ✅ User Interface

* Drag-and-drop file upload

* Drug input field

* Color-coded risk visualization

* Downloadable structured JSON output
---
# 🏗️ System Architecture

## Frontend:

* React.js

* Tailwind CSS

* Framer Motion (UI animations)

## Backend:

* Python Flask API

* VCF processing pipeline

* Risk prediction logic

## Data & AI:

* Pharmacogenomic variant mapping

* Machine Learning / AI explanation module

## Deployment:

* Cloud hosted web app
---
# 💻 Tech Stack
## Frontend

* React.js

* JavaScript / TypeScript

* Tailwind CSS

## Backend

* Python

* Flask

* REST API

## AI / Data

* Pharmacogenomics datasets

* LLM integration

* Data analysis pipeline

## Tools & Deployment

* GitHub

* Cloud hosting (Vercel / Render / Netlify etc.)

#📥 Installation & Setup
## Clone repository
https://github.com/Chandan-N-2004/RIFT2026_AI_HUNTERS

## Navigate to project folder
cd YOUR_REPO

## Backend setup
pip install -r requirements.txt
python app.py

# #Frontend setup
cd frontend
npm install
npm run dev

# 🌐 Live Demo

## 👉 Live Application:
https://rift-2026-ai-hunters.vercel.app/

# 🎥 Demo Video

## 👉 LinkedIn Demo Video:
https://linkedin.com/your-demo-video

# 📊 Usage Guide

1. Upload VCF genetic data file

2. Enter drug name(s)

3. Click analyze

4. View personalized risk assessment

5. Download clinical report (JSON)

# 📁 Project Structure
PharmaGuard/
│
├── frontend/
├── backend/
├── data/
├── docs/
├── requirements.txt
└── README.md

# 🧪 Example Output
{
  "patient_id": "PATIENT_001",
  "drug": "CODEINE",
  "risk_label": "Adjust Dosage",
  "confidence_score": 0.92
}
# 🔐 Disclaimer

This project is for research, educational, and hackathon purposes only.
It is not a clinical diagnostic tool.

# 👥 Team Members
## 👨‍💻 Authors

Bhoomika – Data Analysis

Chandan – Frontend Developer

Charan – Backend Developer

Nitya – Backend Developer


# 📧 Contact Emails

chandan2004.n@email.com

charankumarkh910@email.com

nityanama101@email.com

asbhoomika51@email.com

# ⭐ Acknowledgements

* Hackathon organizers

* Pharmacogenomics research community

* Open-source contributors

# 📜 License

This project is licensed under the MIT License.
