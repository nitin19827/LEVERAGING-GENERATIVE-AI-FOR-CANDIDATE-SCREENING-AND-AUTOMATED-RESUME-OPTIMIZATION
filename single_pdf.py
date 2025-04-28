import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import io  # Add io import at the top level
import re  # Add re import for regex

# Load environment variables at the module level
load_dotenv()

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

def student_portal():
    global os  # Explicitly declare os as global
    # Configure the API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not set in the environment variables!")
        return
    genai.configure(api_key=api_key)

    # Feature selection in sidebar
    feature = st.sidebar.selectbox(
        "Select Feature",
        [
            "Resume Analysis",
            "Skill Gap Analysis",
            "Interview Preparation",
            "Project Portfolio Builder",
            "Career Path Visualization"
        ]
    )

    # Common functions
    @st.cache_data(show_spinner=False)
    def extract_pdf_text(uploaded_files):
        text = ""
        for pdf_file in uploaded_files:
            try:
                # Create BytesIO object from the uploaded file
                from io import BytesIO
                pdf_bytes = BytesIO(pdf_file.getvalue() if hasattr(pdf_file, 'getvalue') else pdf_file)
                
                # Try to read the PDF
                try:
                    reader = pdf.PdfReader(pdf_bytes)
                    
                    # Check if PDF is valid and has pages
                    if len(reader.pages) > 0:
                        for page in reader.pages:
                            try:
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n"
                            except Exception as page_error:
                                st.warning(f"Could not extract text from a page: {str(page_error)}")
                                continue
                    else:
                        st.warning("PDF has no readable pages")
                        continue
                            
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
                    continue
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                continue
                
        return text if text else "No text could be extracted from the PDF files."

    @st.cache_data(show_spinner=False)
    def get_gemini_response(input_text, pdf_content, prompt):
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([input_text, pdf_content, prompt])
        return response.text

    # Resume Analysis Feature
    if feature == "Resume Analysis":
        st.title("Leveraging Generative AI for Candidate Screening and Automated Resume Optimization")
        st.text("Improve Your Resume ATS")
        
        # Input fields
        jd = st.text_area("Paste the Job Description")
        uploaded_files = st.file_uploader("Upload Your Resume(s)", type=["pdf"], help="Please upload PDF(s)", accept_multiple_files=True)
        
        # Button actions
        submit1 = st.button("Tell Me About the Resume")
        submit2 = st.button("How Can I Improve My Skills")
        submit3 = st.button("What Keywords Are Missing")
        submit4 = st.button("Percentage Match")
        input_prompt = st.text_input("Queries: Feel Free to Ask Here")
        submit5 = st.button("Answer My Query")
        
        # Prompt templates
        input_prompts = {
            "submit1": """
            You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
            Please share your professional evaluation on whether the candidate's profile aligns with the role.
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """,
            "submit2": """
            You are a Technical Human Resource Manager with expertise in data science. Your role is to scrutinize the resume in light of the job description provided.
            Share your insights on the candidate's suitability for the role from an HR perspective.
            Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
            """,
            "submit3": """
            You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
            Your task is to evaluate the resume against the provided job description. Assess the compatibility of the resume with the role.
            Provide the missing keywords and recommendations for enhancing the candidate's skills, and identify areas for improvement.
            """,
            "submit4": """
            You are a skilled ATS (Applicant Tracking System) scanner with expertise in data science and ATS functionality.
            Your task is to evaluate the resume against the provided job description. Provide the percentage match between the resume and the job description.
            First, display the percentage match, then list the missing keywords, and finally share your overall evaluation.
            """
        }

        # Process inputs and generate response if both job description and resume(s) are provided
        if uploaded_files and jd:
            resume_text = extract_pdf_text(uploaded_files)
            if submit1:
                response = get_gemini_response(jd, resume_text, input_prompts["submit1"])
                st.subheader(response)
            elif submit2:
                response = get_gemini_response(jd, resume_text, input_prompts["submit2"])
                st.subheader(response)
            elif submit3:
                response = get_gemini_response(jd, resume_text, input_prompts["submit3"])
                st.subheader(response)
            elif submit4:
                response = get_gemini_response(jd, resume_text, input_prompts["submit4"])
                st.subheader(response)
            elif submit5 and input_prompt:
                response = get_gemini_response(jd, resume_text, input_prompt)
                st.subheader(response)
        else:
            if submit1 or submit2 or submit3 or submit4 or submit5:
                st.warning("Please provide both a job description and upload at least one resume.")

    # Skill Gap Analysis Feature
    elif feature == "Skill Gap Analysis":
        st.title("Skill Gap Analysis")
        st.write("Analyze the gap between your current skills and job requirements")
        
        jd = st.text_area("Paste the Job Description")
        current_skills = st.text_area("List your current skills (comma separated)")
        uploaded_files = st.file_uploader("Upload Your Resume (Optional)", type=["pdf"], help="Upload your resume for more detailed analysis")
        
        if st.button("Analyze Skill Gaps"):
            if jd and current_skills:
                resume_text = ""
                if uploaded_files:
                    resume_text = extract_pdf_text([uploaded_files])  # Wrap in list to match function signature
                
                analysis = get_gemini_response(jd, f"Current Skills: {current_skills}\nResume: {resume_text}", """
                Analyze the gap between the candidate's current skills and the job requirements.
                Provide a detailed analysis including:
                1. Missing skills that are crucial for this role
                2. Resources to learn these skills (free and paid)
                3. Estimated time to acquire each skill
                4. Priority order for learning
                5. How to highlight transferable skills
                6. Action plan for skill development
                """)
                st.write(analysis)
            else:
                st.warning("Please provide both a job description and your current skills.")

    # Interview Preparation Feature
    elif feature == "Interview Preparation":
        st.title("Interview Preparation Assistant")
        st.write("Get personalized interview preparation based on your resume and job description")
        
        jd = st.text_area("Paste the Job Description")
        uploaded_files = st.file_uploader("Upload Your Resume", type=["pdf"], help="Upload your resume for personalized questions")
        interview_type = st.selectbox("Select Interview Type", 
                                    ["Technical", "Behavioral", "System Design", "Case Study", "All Types"])
        
        if st.button("Generate Practice Questions"):
            if jd and uploaded_files:
                resume_text = extract_pdf_text([uploaded_files])  # Wrap in list to match function signature
                questions = get_gemini_response(jd, resume_text, f"""
                Generate comprehensive interview preparation for {interview_type} interviews based on the job description and resume.
                Include:
                1. 5 relevant interview questions
                2. What the interviewer is looking for in each question
                3. Sample answers
                4. Key points to cover
                5. Common mistakes to avoid
                6. Follow-up questions to expect
                7. Tips for answering effectively
                """)
                st.write(questions)
            else:
                st.warning("Please provide both a job description and upload your resume.")

    # Project Portfolio Builder Feature
    elif feature == "Project Portfolio Builder":
        st.title("Project Portfolio Builder")
        st.write("Enhance your project descriptions and generate a beautiful portfolio website")
        
        jd = st.text_area("Paste the Job Description")
        project_description = st.text_area("Describe your project in detail", height=200)
        uploaded_files = st.file_uploader("Upload Your Resume (Optional)", type=["pdf"], help="Upload your resume for context")
        
        # Additional project details
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name", key="project_name")
            project_tech = st.text_input("Technologies Used (comma separated)", key="project_tech")
            project_duration = st.text_input("Project Duration", key="project_duration")
        with col2:
            project_role = st.text_input("Your Role in Project", key="project_role")
            project_team = st.text_input("Team Size", key="project_team")
            project_link = st.text_input("Project Link (if any)", key="project_link")
        
        if st.button("Generate Portfolio Website"):
            if project_description and project_name:  # Only require project name and description as minimum
                resume_text = ""
                if uploaded_files:
                    resume_text = extract_pdf_text([uploaded_files])
                
                # Generate enhanced project description
                enhanced = get_gemini_response(jd, f"Project: {project_description}\nResume: {resume_text}", """
                Enhance this project description to make it more impactful for the job application.
                Include:
                1. Business impact and value created
                2. Technical challenges overcome
                3. Key achievements and results
                4. Skills demonstrated
                5. Metrics and quantifiable outcomes
                6. Team collaboration aspects
                7. Learning outcomes
                8. STAR format (Situation, Task, Action, Result)
                """)

                # Generate best features
                best_features = get_gemini_response(jd, f"Project: {project_description}\nResume: {resume_text}", """
                List the best features and highlights of this project in bullet points.
                Focus on:
                1. Technical innovations
                2. User experience improvements
                3. Performance optimizations
                4. Unique solutions
                5. Scalability aspects
                """)

                # Generate portfolio website
                template = '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{project_name} - Project Portfolio</title>
                    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                            font-family: 'Poppins', sans-serif;
                        }}
                        
                        body {{
                            background: linear-gradient(135deg, #1a1a2e, #16213e);
                            color: #fff;
                            line-height: 1.6;
                        }}
                        
                        .container {{
                            max-width: 1200px;
                            margin: 0 auto;
                            padding: 2rem;
                        }}
                        
                        header {{
                            text-align: center;
                            padding: 4rem 0;
                            animation: fadeIn 1s ease-in;
                        }}
                        
                        h1 {{
                            font-size: 3rem;
                            margin-bottom: 1rem;
                            background: linear-gradient(45deg, #00f2fe, #4facfe);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }}
                        
                        .project-info {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                            gap: 2rem;
                            margin: 3rem 0;
                            animation: slideUp 1s ease-in;
                        }}
                        
                        .info-card {{
                            background: rgba(255, 255, 255, 0.1);
                            padding: 1.5rem;
                            border-radius: 10px;
                            backdrop-filter: blur(10px);
                            transition: transform 0.3s ease;
                        }}
                        
                        .info-card:hover {{
                            transform: translateY(-5px);
                        }}
                        
                        .project-details {{
                            background: rgba(255, 255, 255, 0.05);
                            padding: 2rem;
                            border-radius: 15px;
                            margin: 2rem 0;
                            animation: slideUp 1.2s ease-in;
                        }}
                        
                        .tech-stack {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 1rem;
                            margin: 1rem 0;
                        }}
                        
                        .tech-item {{
                            background: rgba(0, 242, 254, 0.2);
                            padding: 0.5rem 1rem;
                            border-radius: 20px;
                            font-size: 0.9rem;
                        }}

                        .project-overview {{
                            margin: 2rem 0;
                        }}

                        .project-overview p {{
                            margin-bottom: 1.5rem;
                            text-align: justify;
                            padding-left: 0;
                        }}

                        .best-features {{
                            margin: 2rem 0;
                        }}

                        .best-features ul {{
                            list-style-type: none;
                            padding-left: 0;
                        }}

                        .best-features li {{
                            margin-bottom: 1rem;
                            padding-left: 0;
                            position: relative;
                        }}

                        .best-features li:before {{
                            content: "";
                            display: none;
                        }}
                        
                        @keyframes fadeIn {{
                            from {{ opacity: 0; }}
                            to {{ opacity: 1; }}
                        }}
                        
                        @keyframes slideUp {{
                            from {{ transform: translateY(50px); opacity: 0; }}
                            to {{ transform: translateY(0); opacity: 1; }}
                        }}
                        
                        .highlight {{
                            color: #00f2fe;
                            font-weight: 500;
                        }}
                        
                        footer {{
                            text-align: center;
                            padding: 2rem 0;
                            margin-top: 3rem;
                            border-top: 1px solid rgba(255, 255, 255, 0.1);
                        }}

                        .project-link {{
                            margin-top: 2rem;
                            padding: 1rem;
                            background: rgba(255, 255, 255, 0.05);
                            border-radius: 10px;
                        }}

                        .project-link a {{
                            display: inline-block;
                            margin-top: 0.5rem;
                            padding: 0.5rem 1rem;
                            background: rgba(0, 242, 254, 0.2);
                            border-radius: 20px;
                            text-decoration: none;
                            transition: all 0.3s ease;
                        }}

                        .project-link a:hover {{
                            background: rgba(0, 242, 254, 0.3);
                            transform: translateY(-2px);
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <header>
                            <h1>{project_name}</h1>
                            <p class="highlight">A showcase of innovation and technical excellence</p>
                        </header>
                        
                        <div class="project-info">
                            <div class="info-card">
                                <h3>Project Duration</h3>
                                <p>{project_duration}</p>
                            </div>
                            <div class="info-card">
                                <h3>Role</h3>
                                <p>{project_role}</p>
                            </div>
                            <div class="info-card">
                                <h3>Team Size</h3>
                                <p>{project_team}</p>
                            </div>
                        </div>
                        
                        <div class="project-details">
                            <h2>Project Overview</h2>
                            <div class="project-overview">
                                {enhanced_text}
                            </div>
                            
                            <h2>Best Features</h2>
                            <div class="best-features">
                                {best_features_text}
                            </div>
                            
                            <h3>Technologies Used</h3>
                            <div class="tech-stack">
                                {tech_stack_html}
                            </div>
                            
                            {project_link_html}
                        </div>
                    </div>
                    
                    <footer>
                        <p>© {project_name} Portfolio | Designed with ❤️</p>
                    </footer>
                    
                    <script>
                        // Add scroll animations
                        document.addEventListener('DOMContentLoaded', () => {{
                            const observer = new IntersectionObserver((entries) => {{
                                entries.forEach(entry => {{
                                    if (entry.isIntersecting) {{
                                        entry.target.style.opacity = '1';
                                        entry.target.style.transform = 'translateY(0)';
                                    }}
                                }});
                            }}, {{ threshold: 0.1 }});
                            
                            document.querySelectorAll('.info-card, .project-details').forEach(el => {{
                                el.style.opacity = '0';
                                el.style.transform = 'translateY(20px)';
                                el.style.transition = 'all 0.6s ease-out';
                                observer.observe(el);
                            }});
                        }});
                    </script>
                </body>
                </html>
                '''

                # Prepare the content
                enhanced_text = enhanced.replace('**', '').replace('\n', '</p><p>')
                enhanced_text = '<p>' + enhanced_text + '</p>'
                
                # Remove stars from best features and clean up
                best_features_text = best_features.replace('**', '')
                best_features_text = '<ul><li>' + best_features_text.replace('\n', '</li><li>') + '</li></ul>'
                tech_stack_html = ''.join([f'<span class="tech-item">{tech.strip()}</span>' for tech in project_tech.split(',')])
                
                # Only create project link HTML if a link is provided
                project_link_html = ''
                if project_link and project_link.strip():
                    project_link_html = f'''
                    <div class="project-link">
                        <h3>Project Link</h3>
                        <a href="{project_link}" class="highlight" target="_blank">View Live Project</a>
                    </div>
                    '''

                # Format the template
                portfolio_html = template.format(
                    project_name=project_name,
                    project_duration=project_duration if project_duration else "Not specified",
                    project_role=project_role if project_role else "Not specified",
                    project_team=project_team if project_team else "Not specified",
                    enhanced_text=enhanced_text,
                    best_features_text=best_features_text,
                    tech_stack_html=tech_stack_html,
                    project_link_html=project_link_html
                )
                
                # Display the values for debugging
                st.write("### Debug Information")
                st.write(f"Project Duration: {project_duration}")
                st.write(f"Role: {project_role}")
                st.write(f"Team Size: {project_team}")
                st.write(f"Technologies: {project_tech}")
                
                # Save the portfolio website
                import os
                portfolio_dir = "portfolio_websites"
                if not os.path.exists(portfolio_dir):
                    os.makedirs(portfolio_dir)
                
                # Sanitize the project name for the filename
                sanitized_project_name = sanitize_filename(project_name)
                portfolio_path = os.path.join(portfolio_dir, f"{sanitized_project_name.lower()}_portfolio.html")
                with open(portfolio_path, "w", encoding="utf-8") as f:
                    f.write(portfolio_html)
                
                # Display enhanced description and portfolio
                st.write("### Enhanced Project Description")
                st.write(enhanced)
                
                st.write("### Your Portfolio Website")
                # Display the portfolio content directly in Streamlit
                st.markdown(portfolio_html, unsafe_allow_html=True)
                
                # Provide download option
                with open(portfolio_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="Download Portfolio Website",
                        data=f.read(),
                        file_name=f"{sanitized_project_name.lower()}_portfolio.html",
                        mime="text/html"
                    )
                
            else:
                st.warning("Please provide at least the project name, description, and job description.")

    # Career Path Visualization Feature
    elif feature == "Career Path Visualization":
        st.title("Career Path Visualization")
        st.write("Get a personalized career development plan")
        
        jd = st.text_area("Paste the Job Description")
        uploaded_files = st.file_uploader("Upload Your Resume", type=["pdf"], help="Upload your resume for personalized career path")
        years_experience = st.number_input("Years of Professional Experience", min_value=0, max_value=50, value=0)
        
        if st.button("Generate Career Path"):
            if jd and uploaded_files:
                resume_text = extract_pdf_text([uploaded_files])  # Wrap in list to match function signature
                path = get_gemini_response(jd, f"Resume: {resume_text}\nExperience: {years_experience} years", """
                Create a comprehensive 5-year career development plan including:
                1. Short-term goals (6 months)
                2. Medium-term goals (1-2 years)
                3. Long-term goals (3-5 years)
                4. Required skills and certifications
                5. Potential career transitions
                6. Salary progression
                7. Industry trends to watch
                8. Networking opportunities
                9. Professional development resources
                10. Risk factors and mitigation strategies
                """)
                st.write(path)
            else:
                st.warning("Please provide both a job description and upload your resume.")

    st.markdown("---", unsafe_allow_html=True)

if __name__ == "__main__":
    student_portal()
