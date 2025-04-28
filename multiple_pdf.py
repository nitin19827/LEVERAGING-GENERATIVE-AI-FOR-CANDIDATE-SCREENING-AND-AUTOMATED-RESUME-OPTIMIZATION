# #multiple resumes but providing only ats score and email



import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import pandas as pd
import json
import re
from dotenv import load_dotenv

def industry_portal():
    # Load environment variables and configure the Generative AI API
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not set in the environment variables!")
        return
    genai.configure(api_key=api_key)
    
    st.title("Leveraging Generative AI for Candidate Screening and Automated Resume Optimization")
    st.write(
        "Upload a folder of resumes along with a job description. The system will process each resume based on your query.\n\n"
    )
    
    # Input fields
    jd = st.text_area("Job Description", placeholder="Paste the job description here...")
    uploaded_files = st.file_uploader("Upload Resumes (PDFs)", type="pdf", accept_multiple_files=True)
    query = st.text_area("Enter your Query", 
                         placeholder="Screen the resumes with ATS score more than 40%, who have graduated from top institutions like Meghnad Saha Institute of Tecchnology")
    
    # Extract criteria from the query (threshold and required college)
    threshold_val = None
    required_college = None
    try:
        threshold_match = re.search(r"ATS\s*score\s*more\s*than\s*(\d+)", query, re.IGNORECASE)
        if threshold_match:
            threshold_val = float(threshold_match.group(1))
    except Exception as e:
        st.write("Could not extract ATS score threshold:", e)
    
    try:
        college_match = re.search(r"graduated\s*from\s*top\s*institutions\s*like\s*([^,]+)", query, re.IGNORECASE)
        if college_match:
            required_college = college_match.group(1).strip()
    except Exception as e:
        st.write("Could not extract required college:", e)
    
    if st.button("Process Resumes"):
        if not jd or not uploaded_files or not query:
            st.warning("Please provide a job description, upload at least one resume, and enter a query.")
            return
        
        filtered_results = []
        
        @st.cache_data(show_spinner=False)
        def extract_pdf_text(pdf_file):
            try:
                reader = pdf.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as e:
                st.error(f"Error reading {pdf_file.name}: {e}")
                return ""
        
        @st.cache_data(show_spinner=False)
        def get_gemini_response(input_text, pdf_content, prompt):
            model = genai.GenerativeModel('gemini-2.0-flash')  # Update model name if needed
            response = model.generate_content([input_text, pdf_content, prompt])
            return response.text
        
        def clean_json_response(response_text):
            cleaned = response_text.strip()
            # Remove markdown code fences if present (e.g., ```json ... ``` )
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            return cleaned
        
        # Process each uploaded resume
        for pdf_file in uploaded_files:
            resume_text = extract_pdf_text(pdf_file)
            if not resume_text:
                continue
            
            # New prompt: instruct the model to return all required details.
            prompt = f"""
You are an expert recruiter. Evaluate the resume based solely on the following query:
"{query}"

Ignore all other details.

Given the job description:
{jd}

And the resume content:
{resume_text}

Based on the above, please:
- Calculate the ATS match score as a numeric percentage (0 to 100).
- Determine if the resume meets the criteria (return "Yes" if it does, otherwise "No").
- Identify the candidate's College.
- Extract the candidate's CGPA.
- List any Certifications.
- Provide the candidate's Email.

Return your answer strictly in JSON format with only these keys:
- "Match": "Yes" or "No"
- "ATS Score": (numeric percentage or "N/A")
- "College": (the name of the college or "N/A")
- "CGPA": (numeric value or "N/A")
- "Certifications": (a list of certifications or "N/A")
- "Candidate Email": (the candidate's email or "N/A")

Ensure the JSON is valid.
            """
            try:
                response_text = get_gemini_response(jd, resume_text, prompt)
            except Exception as e:
                st.error(f"Error processing {pdf_file.name}: {e}")
                continue
            
            st.write(f"Raw response for {pdf_file.name}:", response_text)
            
            cleaned_response = clean_json_response(response_text)
            try:
                parsed_response = json.loads(cleaned_response)
            except Exception as e:
                st.error(f"Failed to parse JSON for {pdf_file.name}: {e}")
                parsed_response = {
                    "Match": "Parsing Error",
                    "ATS Score": "N/A",
                    "College": "N/A",
                    "CGPA": "N/A",
                    "Certifications": "N/A",
                    "Candidate Email": "N/A"
                }
            
            # If ATS Score is missing or "N/A", attempt to extract a percentage from the response text
            ats = str(parsed_response.get("ATS Score", "")).strip()
            if ats.upper() == "N/A" or ats == "":
                match_percentage = re.search(r"(\d+(\.\d+)?)\s*%", cleaned_response)
                if match_percentage:
                    parsed_response["ATS Score"] = match_percentage.group(1)
            
            # If the model returns "No", override if our criteria are met
            if parsed_response.get("Match", "").strip().lower() != "yes":
                try:
                    ats_val = float(parsed_response.get("ATS Score", 0))
                except:
                    ats_val = 0
                college_val = parsed_response.get("College", "").strip().lower()
                if threshold_val is not None and ats_val >= threshold_val:
                    if required_college is None or required_college.lower() in college_val:
                        parsed_response["Match"] = "Yes"
            
            # Only include resumes that meet the criteria ("Match": "Yes")
            if parsed_response.get("Match", "").strip().lower() == "yes":
                result = {
                    "File Name": pdf_file.name,
                    "ATS Score": parsed_response.get("ATS Score", "N/A"),
                    "College": parsed_response.get("College", "N/A"),
                    "CGPA": parsed_response.get("CGPA", "N/A"),
                    "Certifications": parsed_response.get("Certifications", "N/A"),
                    "Candidate Email": parsed_response.get("Candidate Email", "N/A")
                }
                filtered_results.append(result)
                st.write(f"Processed {pdf_file.name} (Criteria Met):", result)
            else:
                st.write(f"Processed {pdf_file.name} did not meet the criteria.")
        
        st.write("Final Filtered Results:")
        st.write(filtered_results)
        
        # Export filtered results to Excel if available
        if filtered_results:
            df = pd.DataFrame(filtered_results)
            output_file = "Industry_Results.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button("Download Results as Excel", data=file.read(), file_name=output_file)
        else:
            st.info("No resumes matched the query criteria.")

if __name__ == "__main__":
    industry_portal()

