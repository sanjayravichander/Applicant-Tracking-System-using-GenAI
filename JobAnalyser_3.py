import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
from fpdf import FPDF
import base64
from fpdf.enums import XPos, YPos
import requests
from io import BytesIO
import os
import hashlib
import pandas as pd

# Set Streamlit page config
st.set_page_config(page_title="Resume Enhancer and ATS Tracker", layout="wide")
st.header("ATS Tracking System with Resume Enhancer")

# Load API key securely from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# Function to extract text from the uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in pdf_document])
        return text
    else:
        raise FileNotFoundError("No File uploaded")

# Track and retrieve cached responses
@st.cache_data
def get_cached_response(resume_text, job_desc, prompt_type, prompt_text):
    key = hashlib.sha256((resume_text + job_desc + prompt_type).encode('utf-8')).hexdigest()
    return st.session_state.get(key)

@st.cache_data
def save_response(resume_text, job_desc, prompt_type, prompt_text, result):
    key = hashlib.sha256((resume_text + job_desc + prompt_type).encode('utf-8')).hexdigest()
    st.session_state[key] = result

    # Track analysis count
    st.session_state.analysis_count[key] = st.session_state.analysis_count.get(key, 0) + 1

    # Track log
    st.session_state.analysis_log.append({
        "Key": key,
        "Prompt Type": prompt_type,
        "Job Description": job_desc[:100],
        "Resume Snippet": resume_text[:100],
        "Times Analyzed": st.session_state.analysis_count[key]
    })

# Function to get AI response from Groq API
def get_response_with_retry(input_text, pdf_text, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an experienced ATS resume evaluator."},
                    {"role": "user", "content": input_text},
                    {"role": "user", "content": pdf_text},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
            else:
                st.error("An internal server error occurred. Please try again later.")
                return None

# Function to download and cache Unicode font
@st.cache_resource
def get_unicode_font_path():
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Font not found at: {font_path}")
    return font_path

# Function to create professional PDF resume
def create_pdf(resume_content):
    pdf = FPDF()
    pdf.add_page()
    regular_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    bold_path = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")
    pdf.add_font("DejaVu", "", fname=regular_path, uni=True)
    pdf.add_font("DejaVu", "B", fname=bold_path, uni=True)
    pdf.set_font("DejaVu", "", 12)

    for line in resume_content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.endswith(':'):
            pdf.set_font("DejaVu", "B", 14)
            pdf.cell(0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", "", 12)
            pdf.ln(3)
        elif line.startswith('•'):
            pdf.set_font("DejaVu", "", 11)
            pdf.cell(10)
            pdf.multi_cell(0, 7, line)
            pdf.ln(2)
        else:
            pdf.set_font("DejaVu", "", 12)
            pdf.multi_cell(0, 8, line)
            pdf.ln(3)

    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin1')
    elif isinstance(output, bytearray):
        return bytes(output)
    else:
        return output

# Initialize tracking states
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = {}

if 'analysis_log' not in st.session_state:
    st.session_state.analysis_log = []

# UI elements
input_text = st.text_area("Enter Job Description:", key="input", height=150)
uploaded_file = st.file_uploader("Upload a PDF Resume", type=["pdf"])
if uploaded_file:
    st.success("PDF uploaded successfully ✅")

# Action buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    submit1 = st.button("Tell me about the Resume")
with col2:
    submit2 = st.button("Improvement Suggestions")
with col3:
    submit3 = st.button("Match Percentage")
with col4:
    submit4 = st.button("Generate Tailored Resume")
with col5:
    export_log = st.button("📤 Export Log as CSV")

# Prompts
input_prompt1 = """
You're an experienced Technical Human Resource Manager. Review the provided resume against the job description.
Highlight key matches, any skill gaps, and suggest improvements.
"""
input_prompt2 = """
As a technical HR expert, assess the resume for job fit. 
Share insights on the candidate's sustainability for the role and specific improvement suggestions.
"""
input_prompt3 = """
You are an ATS scanner. Evaluate the resume against the job description.
Provide a percentage match, missing keywords, and final thoughts.
"""
input_prompt4 = """
You are a professional resume enhancer.

Instructions:
1. Maintain the original resume format, tone, and section order.
2. Keep all real personal details, education, and experience **unchanged**.
3. Under the "PROJECTS" section, **replace all existing projects** with 4 new **mock projects** that match the job description.
4. Each mock project should:
   - Have a clear title (no headings like “Mock Project” or “Enhanced Project”)
   - Include 4–5 bullet points (use •) that are **detailed and realistic**
   - Be aligned with the job description
5. DO NOT:
   - Add headings like “Enhanced Projects”
   - Include any commentary or labels in the output
   - Keep the original projects
6. Output only the full resume content.
"""

# Button logic
if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)

    if submit1:
        prompt_type = "submit1"
        cached = get_cached_response(pdf_text, input_text, prompt_type, input_prompt1)
        if cached:
            response = cached
        else:
            response = get_response_with_retry(input_text, pdf_text, input_prompt1)
            if response:
                save_response(pdf_text, input_text, prompt_type, input_prompt1, response)
        if response:
            st.subheader("Resume Analysis")
            st.write(response)

    if submit2:
        prompt_type = "submit2"
        cached = get_cached_response(pdf_text, input_text, prompt_type, input_prompt2)
        if cached:
            response = cached
        else:
            response = get_response_with_retry(input_text, pdf_text, input_prompt2)
            if response:
                save_response(pdf_text, input_text, prompt_type, input_prompt2, response)
        if response:
            st.subheader("Improvement Suggestions")
            st.write(response)

    if submit3:
        prompt_type = "submit3"
        cached = get_cached_response(pdf_text, input_text, prompt_type, input_prompt3)
        if cached:
            response = cached
        else:
            response = get_response_with_retry(input_text, pdf_text, input_prompt3)
            if response:
                save_response(pdf_text, input_text, prompt_type, input_prompt3, response)
        if response:
            st.subheader("ATS Match Analysis")
            st.write(response)

    if submit4:
        prompt_type = "submit4"
        full_prompt = input_prompt4 + "\n\nJob Description:\n" + input_text + "\n\nResume:\n" + pdf_text
        cached = get_cached_response(pdf_text, input_text, prompt_type, full_prompt)
        if cached:
            response = cached
        else:
            response = get_response_with_retry(input_text, pdf_text, full_prompt)
            if response:
                save_response(pdf_text, input_text, prompt_type, full_prompt, response)
        if response:
            st.subheader("🎯 Generated Tailored Resume")
            st.text_area("Preview of Enhanced Resume", response, height=500)

            try:
                pdf_bytes = create_pdf(response)
                st.download_button(
                    label="📥 Download Enhanced Resume as PDF",
                    data=pdf_bytes,
                    file_name="professional_resume.pdf",
                    mime="application/pdf"
                )
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

# Export log as CSV
if export_log:
    if st.session_state.analysis_log:
        df = pd.DataFrame(st.session_state.analysis_log)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📁 Download Analysis Log", csv, "analysis_log.csv", "text/csv")
    else:
        st.info("No analysis history available to export.")
