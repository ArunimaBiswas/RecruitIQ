import streamlit as st
import requests
import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Configure Streamlit page
st.set_page_config(
    page_title="RecruitIQ",
    page_icon="👔",
    layout="wide"
)

# API Configuration
API_URL = "http://localhost:5000/api"

# Google OAuth Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_google():
    """Handle Google OAuth authentication"""
    creds = None
    
    # Check if we have stored credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are not valid or don't exist, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .match-score {
        font-size: 24px;
        font-weight: bold;
    }
    .high-match {
        color: green;
    }
    .medium-match {
        color: orange;
    }
    .low-match {
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Create Job", "Apply for Job", "View Candidates", "Schedule Interview"]
)

# Helper Functions
def get_match_score_color(score):
    if score >= 0.7:
        return "high-match"
    elif score >= 0.4:
        return "medium-match"
    return "low-match"

# Create Job Page
if page == "Create Job":
    st.title("Create New Job Posting")
    
    with st.form("job_form"):
        title = st.text_input("Job Title")
        description = st.text_area("Job Description", height=200)
        submit = st.form_submit_button("Create Job")
        
        if submit:
            if title and description:
                response = requests.post(
                    f"{API_URL}/jobs",
                    json={"title": title, "description": description}
                )
                
                if response.status_code == 201:
                    st.success(f"Job created successfully! Job ID: {response.json()['job_id']}")
                else:
                    st.error("Failed to create job. Please try again.")
            else:
                st.warning("Please fill in all fields.")

# Apply for Job Page
elif page == "Apply for Job":
    st.title("Apply for a Job")
    
    with st.form("apply_form"):
        job_id = st.number_input("Job ID", min_value=1)
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        resume = st.file_uploader("Upload Resume (PDF)", type="pdf")
        submit = st.form_submit_button("Submit Application")
        
        if submit:
            if name and email and resume and job_id:
                files = {"resume": (resume.name, resume, "application/pdf")}
                data = {
                    "job_id": job_id,
                    "name": name,
                    "email": email
                }
                
                response = requests.post(
                    f"{API_URL}/apply",
                    files=files,
                    data=data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    st.success("Application submitted successfully!")
                    st.markdown(f"""
                        <div class="match-score {get_match_score_color(result['match_score'])}">
                            Match Score: {result['match_score']:.2%}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Failed to submit application. Please try again.")
            else:
                st.warning("Please fill in all fields and upload a resume.")

# View Candidates Page
elif page == "View Candidates":
    st.title("View Candidates")
    
    job_id = st.number_input("Job ID", min_value=1)
    if st.button("Fetch Candidates"):
        response = requests.get(f"{API_URL}/jobs/{job_id}/candidates")
        
        if response.status_code == 200:
            candidates = response.json()
            
            for candidate in candidates:
                with st.expander(f"{candidate['name']} - Match Score: {candidate['match_score']:.2%}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Contact Information**")
                        st.write(f"Email: {candidate['email']}")
                        st.write(f"Status: {candidate['status']}")
                    
                    with col2:
                        st.write("**Match Details**")
                        match_details = candidate['match_details']
                        
                        st.write("**Matching Skills:**")
                        for skill in match_details['matching_skills']:
                            st.write(f"✅ {skill}")
                        
                        st.write("**Missing Skills:**")
                        for skill in match_details['missing_skills']:
                            st.write(f"❌ {skill}")
                        
                        if match_details['matching_education']:
                            st.write("**Matching Education:**")
                            for edu in match_details['matching_education']:
                                st.write(f"✅ {edu}")
                        
                        if match_details['missing_education']:
                            st.write("**Missing Education:**")
                            for edu in match_details['missing_education']:
                                st.write(f"❌ {edu}")
        else:
            st.error("Failed to fetch candidates. Please try again.")

# Schedule Interview Page
elif page == "Schedule Interview":
    st.title("Schedule Interview")
    
    # Check Google authentication
    if not os.path.exists('token.pickle'):
        st.warning("Please authenticate with Google to schedule interviews.")
        if st.button("Authenticate with Google"):
            try:
                authenticate_google()
                st.success("Successfully authenticated with Google!")
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
    else:
        application_id = st.number_input("Application ID", min_value=1)
        if st.button("Schedule Interview"):
            response = requests.post(
                f"{API_URL}/schedule",
                json={"application_id": application_id}
            )
            
            if response.status_code == 201:
                result = response.json()
                interview_time = datetime.fromisoformat(result['interview_time'])
                st.success(f"""
                    Interview scheduled successfully!
                    Date and Time: {interview_time.strftime('%B %d, %Y at %I:%M %p')}
                """)
            else:
                st.error("Failed to schedule interview. Please try again.")

# Run with: streamlit run streamlit_app.py 