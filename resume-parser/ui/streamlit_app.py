import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Resume Parser Demo",
    page_icon="Resume",
    layout="wide"
)

st.title("Resume Parsing System")
st.markdown("Upload a PDF or DOCX resume to extract its key information securely using Local LLMs.")

st.sidebar.header("Upload File")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['pdf', 'docx', 'doc'])

if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'document_id' not in st.session_state:
    st.session_state.document_id = None

if uploaded_file is not None:
    if st.sidebar.button("Extract Information"):
        with st.spinner("Processing resume..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
                response = requests.post(f"{API_URL}/api/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.parsed_data = result.get("data")
                    st.session_state.document_id = result.get("document_id")
                    st.success("Extraction complete!")
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend API. Is the FastAPI server running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

if st.session_state.parsed_data:
    data = st.session_state.parsed_data
    
    st.subheader("Extracted Details")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Contact Information")
        contact = data.get("contact_information", {})
        if contact:
            st.write(f"**Name:** {contact.get('name')}")
            st.write(f"**Email:** {contact.get('email')}")
            st.write(f"**Phone:** {contact.get('phone')}")
            st.write(f"**Location:** {contact.get('location')}")
        else:
            st.info("No contact information found.")
            
        st.markdown("### Professional Summary")
        summary = data.get("professional_summary")
        if summary:
            st.info(summary)
        else:
            st.info("No professional summary found.")
            
        st.markdown("### Skills")
        skills = data.get("skills", [])
        if skills:
            # Displaying skills as tags
            html_skills = "".join([f"<span style='background-color:#007bff;color:white;padding:2px 8px;border-radius:15px;margin-right:5px;display:inline-block;margin-bottom:5px'>{skill}</span>" for skill in skills])
            st.markdown(html_skills, unsafe_allow_html=True)
        else:
            st.info("No skills found.")
            
        st.markdown("### Certifications")
        certs = data.get("certifications", [])
        if certs:
            for cert in certs:
                st.write(f"- {cert}")
        else:
            st.info("No certifications found.")
            
            
    with col2:
        st.markdown("### Work Experience & Projects")
        experience = data.get("work_experience", [])
        if experience:
            for i, exp in enumerate(experience):
                is_proj = exp.get("is_project", False)
                type_label = "Project" if is_proj else "Role"
                title = f"[{type_label}] {exp.get('role', 'Role')} at {exp.get('company', 'Company')} ({exp.get('duration', 'Duration')})"
                
                with st.expander(title, expanded=(i==0)):
                    for resp in exp.get("responsibilities", []):
                        st.write(f"- {resp}")
        else:
            st.info("No work experience or projects found.")
            
        st.markdown("### Education")
        education = data.get("education", [])
        if education:
            for edu in education:
                st.write(f"**{edu.get('degree')}**")
                st.write(f"{edu.get('institution')} | {edu.get('year')}")
                st.write("---")
        else:
            st.info("No education details found.")
            
    st.markdown("---")
    with st.expander("View Raw JSON Output"):
        st.json(data)
