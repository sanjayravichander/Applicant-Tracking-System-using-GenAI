# ATS Resume Expert

The **ATS Resume Expert** is a Streamlit application designed to evaluate resumes against job descriptions using Google Generative AI models. The tool mimics the role of an ATS (Application Tracking System) and a technical HR professional by providing insights into resume-job alignment, areas for improvement, and an overall percentage match.

---

## Features

- **Upload Resume**: Upload a PDF version of your resume for analysis.
- **Job Description Analysis**: Input the job description to evaluate your resume against.
- **Professional Evaluation**:
  - Highlight resume matches with job requirements.
  - Suggest improvements to better align with the job description.
- **Skill Gap Analysis**:
  - Identify skills missing in the resume.
  - Provide actionable feedback to improve resume alignment.
- **Percentage Match**:
  - Evaluate the resume's percentage match with the job description.
  - Highlight missing keywords and provide final recommendations.

---

## How It Works

1. **Resume Upload**: Upload a PDF file of your resume.
2. **Input Job Description**: Provide the job description for the desired role.
3. **AI-Powered Analysis**:
   - Google Generative AI (`gemini-1.5-pro`) processes the resume and job description.
   - Provides detailed feedback based on the selected analysis type:
     - **Resume Evaluation**: Insights into resume-job alignment.
     - **Skill Gap Analysis**: Suggestions for skill improvement.
     - **Percentage Match**: Overall percentage match with missing keywords and explanations.

---

## Requirements

- Python 3.10
- A valid API key for Google Generative AI
- Required Python packages:
  - `streamlit`
  - `google-generativeai`
  - `python-dotenv`
  - `Pillow`
  - `pdf2image`
  - `PyMuPDF` (`fitz`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
