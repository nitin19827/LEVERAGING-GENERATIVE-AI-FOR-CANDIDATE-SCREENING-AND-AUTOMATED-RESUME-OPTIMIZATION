import streamlit as st
from single_pdf import student_portal
from multiple_pdf import industry_portal

def set_custom_style():
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            height: 3em;
            border-radius: 10px;
            font-weight: 500;
            margin-top: 1em;
            background: linear-gradient(45deg, #2193b0, #6dd5ed);
            border: none;
            color: white;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 147, 176, 0.3);
        }
        .portal-card {
            padding: 2em;
            border-radius: 15px;
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            margin: 1em 0;
            transition: transform 0.3s ease;
        }
        .portal-card:hover {
            transform: translateY(-5px);
        }
        .portal-title {
            color: #2193b0;
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 1em;
        }
        .portal-description {
            color: #666;
            margin-bottom: 1em;
        }
        .success-message {
            padding: 1em;
            border-radius: 10px;
            background: linear-gradient(45deg, rgba(33, 147, 176, 0.1), rgba(109, 213, 237, 0.1));
            border-left: 4px solid #2193b0;
            margin: 1em 0;
        }
        .back-button {
            position: fixed;
            top: 1em;
            left: 1em;
            z-index: 1000;
        }
        .main-title {
            background: linear-gradient(45deg, #2193b0, #6dd5ed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1em;
        }
        </style>
    """, unsafe_allow_html=True)

def render_portal_card(title, description, icon):
    st.markdown(f"""
        <div class="portal-card">
            <div class="portal-title">{icon} {title}</div>
            <div class="portal-description">{description}</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Leveraging Generative AI for Candidate Screening and Automated Resume Optimization",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    set_custom_style()
    
    # Initialize session state for page navigation if not already set
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Add back button for non-home pages
    if st.session_state.page != "home":
        st.markdown("""
            <div class="back-button">
                <button onclick="window.history.back()">← Back</button>
            </div>
        """, unsafe_allow_html=True)
    
    # Home page: portal selection
    if st.session_state.page == "home":
        st.markdown('<h1 class="main-title">Leveraging Generative AI for Candidate Screening and Automated Resume Optimization</h1>', unsafe_allow_html=True)
        
        st.markdown("""
            <p style='text-align: center; font-size: 1.2em; color: #666; margin-bottom: 2em;'>
                Welcome to our intelligent resume screening platform. Choose your portal below to get started.
            </p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_portal_card(
                "Student Portal",
                """Perfect for students and job seekers. Upload your resume, analyze it against job descriptions,
                get personalized feedback, and create a beautiful portfolio website.""",
                "👨‍🎓"
            )
            if st.button("Enter Student Portal", key="student_btn"):
                st.session_state.page = "student"
                st.rerun()
        
        with col2:
            render_portal_card(
                "Industry Portal",
                """Designed for recruiters and HR professionals. Upload multiple resumes,
                analyze them in bulk, and find the best candidates for your positions.""",
                "🏢"
            )
            if st.button("Enter Industry Portal", key="industry_btn"):
                st.session_state.page = "industry"
                st.rerun()
        
        # Add features section
        st.markdown("""
            <h2 style='text-align: center; margin-top: 3em; color: #2193b0;'>Key Features</h2>
        """, unsafe_allow_html=True)
        
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        
        with feat_col1:
            st.markdown("""
                ### 🎯 Smart Analysis
                - AI-powered resume screening
                - Skill gap analysis
                - ATS optimization tips
            """)
        
        with feat_col2:
            st.markdown("""
                ### 💼 Career Tools
                - Portfolio generator
                - Interview preparation
                - Career path visualization
            """)
        
        with feat_col3:
            st.markdown("""
                ### 📊 Detailed Insights
                - Skill matching
                - Improvement suggestions
                - Industry trends
            """)
    
    # Display the corresponding page based on the session state
    elif st.session_state.page == "student":
        student_portal()
    
    elif st.session_state.page == "industry":
        industry_portal()

if __name__ == "__main__":
    main()
