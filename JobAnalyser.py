from dotenv import load_dotenv
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import pdf2image
import io
import base64
import fitz  # PyMuPDF
from google.api_core.exceptions import InternalServerError

# Load environment variables
load_dotenv()

# Configure the Google Generative AI API
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Function to get a response from the Google Generative AI model with a retry mechanism
def get_response_with_retry(input, pdf_content, prompt, retries=3):
    model = genai.GenerativeModel("gemini-1.5-pro")
    for attempt in range(retries):
        try:
            response = model.generate_content([input, pdf_content[0], prompt])
            return response.text
        except InternalServerError as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
            else:
                st.error("An internal server error occurred. Please try again later.")
                return None

# Function to process the uploaded PDF file
def setup_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page = pdf_document.load_page(0)
        img_byte_arr = io.BytesIO(first_page.get_pixmap().tobytes("jpeg"))

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": img_byte_arr.getvalue()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No File uploaded")

# Streamlit setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_input("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file is not None:
    st.write("PDF uploaded successfully")

submit1 = st.button("Tell me about the uploaded Resume")
submit2 = st.button("How can I improve my skills?")
submit3 = st.button("Percentage match with the job description")

# Input prompts
input_prompt1 = f"""
You're an experienced Technical Human Resource Manager, and you're tasked to review the provided resume against the job description for these profiles. 
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the major matches and any gaps in the resume.
Also, suggest areas where the resume could be improved to better align with the job description.
Make sure to use specific details from the resume and explain your reasoning.
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
if submit1:
    if uploaded_file is not None:
        pdf_content = setup_pdf(uploaded_file)
        response = get_response_with_retry(input_prompt1, pdf_content, input_text)
        if response:
            st.write(response)
    else:
        st.write("Please upload a PDF file")

elif submit2:
    if uploaded_file is not None:
        pdf_content = setup_pdf(uploaded_file)
        response = get_response_with_retry(input_prompt2, pdf_content, input_text)
        if response:
            st.write(response)
    else:
        st.write("Please upload a PDF file")

elif submit3:
    if uploaded_file is not None:
        pdf_content = setup_pdf(uploaded_file)
        response = get_response_with_retry(input_prompt3, pdf_content, input_text)
        if response:
            st.write(response)
    else:
        st.write("Please upload a PDF file")
