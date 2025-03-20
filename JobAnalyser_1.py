import streamlit as st
import os
import fitz  # PyMuPDF
from openai import OpenAI

# Set Streamlit page config
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Load API key securely from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]

# Configure Groq AI Client
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# Function to extract text from the uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in pdf_document])  # Extract text from all pages
        return text
    else:
        raise FileNotFoundError("No File uploaded")

# Function to get AI response from Groq API
def get_response_with_retry(input_text, pdf_text, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
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

# Streamlit UI elements
input_text = st.text_input("Enter Job Description:", key="input")
uploaded_file = st.file_uploader("Upload a PDF Resume", type=["pdf"])
if uploaded_file:
    st.success("PDF uploaded successfully ✅")

submit1 = st.button("Tell me about the uploaded Resume")
submit2 = st.button("How can I improve my skills?")
submit3 = st.button("Percentage match with the job description")

# Input prompts
input_prompt1 = f"""
You're an experienced Technical Human Resource Manager, and you're tasked to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the major matches and any gaps in the resume.
Suggest areas where the resume could be improved to better align with the job description.
Use bullet points if possible.
Job Description:
{input_text}
"""

input_prompt2 = f"""
You are a technical human resource manager with expertise in all roles. 
Your role is to scrutinize the resume in light of the job description provided.
Share your insights on the candidate's sustainability for the role from an HR perspective.
{input_text}
"""

input_prompt3 = f"""
You are an ATS (Application Tracking System) scanner with a deep understanding of all roles and ATS functionality.
Your job is to evaluate the resume against the provided job description.
Provide a percentage match for the resume. First, the output should come as a percentage match and then explain 
keywords missing and final thoughts.
Job Description:
{input_text}
"""

# Handling button clicks
if submit1 or submit2 or submit3:
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)

        if submit1:
            response = get_response_with_retry(input_text, pdf_text, input_prompt1)
        elif submit2:
            response = get_response_with_retry(input_text, pdf_text, input_prompt2)
        elif submit3:
            response = get_response_with_retry(input_text, pdf_text, input_prompt3)

        if response:
            st.write(response)
    else:
        st.warning("⚠️ Please upload a PDF file first.")
