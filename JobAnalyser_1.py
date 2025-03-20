from dotenv import load_dotenv
import os
import streamlit as st
import openai
import groq
import fitz  # PyMuPDF
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure Groq API
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

# Function to extract text from the uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in pdf_document])  # Extract text from all pages
        return text
    else:
        raise FileNotFoundError("No File uploaded")

# Function to get response from Groq AI with retry mechanism
def get_response_with_retry(job_desc, resume_text, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="Llama3-8b-8192",  # Choose "llama3-8b", "llama3-70b", or "mixtral-8x7b"
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Job Description:\n{job_desc}"},
                    {"role": "user", "content": f"Resume Content:\n{resume_text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
            else:
                st.error("An internal server error occurred. Please try again later.")
                return None

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF uploaded successfully")

submit1 = st.button("Tell me about the uploaded Resume")
submit2 = st.button("How can I improve my skills?")
submit3 = st.button("Percentage match with the job description")

# Input prompts
input_prompt1 = "Analyze this resume against the job description and highlight key matches, missing skills, and improvement areas."
input_prompt2 = "Evaluate this resume and suggest skill improvements for the job description."
input_prompt3 = "Compare the resume and job description, providing a percentage match and missing keywords."

# Handling button clicks
if submit1 or submit2 or submit3:
    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if submit1:
            response = get_response_with_retry(input_text, resume_text, input_prompt1)
        elif submit2:
            response = get_response_with_retry(input_text, resume_text, input_prompt2)
        elif submit3:
            response = get_response_with_retry(input_text, resume_text, input_prompt3)

        if response:
            st.write(response)
    else:
        st.write("Please upload a PDF file")
