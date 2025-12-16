"""
Resume Parser - Streamlit Frontend
A web application for parsing resumes using Google's Gemini API
"""

import streamlit as st
import json
import os
from pathlib import Path
import tempfile
from dotenv import load_dotenv
from resume_parser import ResumeParser, get_file_text

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'parsed_result' not in st.session_state:
        st.session_state.parsed_result = None
    
    if 'parsing_complete' not in st.session_state:
        st.session_state.parsing_complete = False


def display_results(result):
    """Display parsed resume results"""
    import hashlib
    
    # Generate unique key based on result data
    result_hash = hashlib.md5(json.dumps(result, sort_keys=True).encode()).hexdigest()[:8]
    
    st.subheader("📋 Extracted Resume Information")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Personal Information**")
        
        with st.container():
            name = result.get('name') or 'Not found'
            email = result.get('email') or 'Not found'
            phone = result.get('phone') or 'Not found'
            position = result.get('position') or 'Not found'
            experience = result.get('experience') or 'Not found'
            education = result.get('education') or 'Not found'
            
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Email:** {email}")
            st.markdown(f"**Phone:** {phone}")
            st.markdown(f"**Position:** {position}")
            st.markdown(f"**Experience:** {experience}")
            st.markdown(f"**Education:** {education}")
    
    with col2:
        if result.get('summary'):
            st.write("**Professional Summary**")
            st.info(result['summary'])
    
    # Skills section
    st.divider()
    st.write("**Skills**")
    
    skill_col1, skill_col2 = st.columns(2)
    
    with skill_col1:
        st.write("**Primary Skills** (Core Technical Competencies)")
        primary = result.get('primarySkills', [])
        if primary:
            for skill in primary:
                st.markdown(f"- {skill}")
        else:
            st.warning("No primary skills found")
    
    with skill_col2:
        st.write("**Secondary Skills** (Supporting Technologies)")
        secondary = result.get('secondarySkills', [])
        if secondary:
            for skill in secondary:
                st.markdown(f"- {skill}")
        else:
            st.warning("No secondary skills found")
    
    # Skills source
    if result.get('skillsSource'):
        st.divider()
        st.info(f"**How Skills Were Determined:** {result['skillsSource']}")
    
    # Raw JSON view
    with st.expander("📊 View Raw JSON"):
        st.json(result)
    
    # Download options
    st.divider()
    
    # Create markdown version
    md_content = f"""# Resume Parsing Results

## Personal Information
- **Name:** {result.get('name', 'Not found')}
- **Email:** {result.get('email', 'Not found')}
- **Phone:** {result.get('phone', 'Not found')}
- **Position:** {result.get('position', 'Not found')}
- **Experience:** {result.get('experience', 'Not found')}
- **Education:** {result.get('education', 'Not found')}

## Summary
{result.get('summary', 'Not found')}

## Primary Skills
{', '.join(result.get('primarySkills', []))}

## Secondary Skills
{', '.join(result.get('secondarySkills', []))}

## Skills Source
{result.get('skillsSource', 'Not available')}
"""
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.download_button(
            label="📥 Download Markdown",
            data=md_content,
            file_name="resume_parsed.md",
            mime="text/markdown",
            key=f"download_md_{result_hash}"
        )
    
    with col2:
        st.write("✅ Parsing complete!")


def main():
    """Main application"""
    initialize_session_state()
    
    # Load API key from environment
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyATiKthQyRU0BQ4z4TRLpOIrga0JWzEs04')
    
    if not api_key:
        st.error("❌ Error: GEMINI_API_KEY not found in .env file. Please add your API key.")
        return
    
    # Header
    st.title("📄 Resume Parser")
    st.markdown("Extract structured information from your resume using Google's Gemini API")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "📝 Paste Text", "📚 Batch Process"])
    
    with tab1:
        st.subheader("Upload Resume File")
        st.markdown("Supported formats: **TXT**, **PDF**, **DOCX**")
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=["txt", "pdf", "docx"],
            help="Upload your resume in any of the supported formats"
        )
        
        if uploaded_file is not None:
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"📄 File: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            
            with col2:
                if st.button("🚀 Parse Resume", key="parse_upload", use_container_width=True):
                    with st.spinner("Parsing your resume..."):
                        try:
                            # Initialize parser with API key from env
                            parser = ResumeParser(api_key)
                            
                            # Parse the file
                            result = parser.parse_from_file(tmp_path)
                            st.session_state.parsed_result = result
                            st.session_state.parsing_complete = True
                            
                        except Exception as e:
                            st.error(f"❌ Error parsing resume: {str(e)}")
                        
                        finally:
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
            
            if st.session_state.parsing_complete and st.session_state.parsed_result:
                display_results(st.session_state.parsed_result)
    
    with tab2:
        st.subheader("Paste Resume Text")
        st.markdown("Paste your resume content directly in the text area below")
        
        resume_text = st.text_area(
            "Resume Content",
            height=300,
            placeholder="Paste your resume text here...",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🚀 Parse Resume", key="parse_text", use_container_width=True):
                if not resume_text.strip():
                    st.error("❌ Please enter resume text first")
                else:
                    with st.spinner("Parsing your resume..."):
                        try:
                            # Initialize parser with API key from env
                            parser = ResumeParser(api_key)
                            
                            # Parse the text
                            result = parser.parse_resume(resume_text)
                            st.session_state.parsed_result = result
                            st.session_state.parsing_complete = True
                            
                        except Exception as e:
                            st.error(f"❌ Error parsing resume: {str(e)}")
        
        if st.session_state.parsing_complete and st.session_state.parsed_result:
            display_results(st.session_state.parsed_result)
    
    with tab3:
        st.subheader("Batch Process Multiple Resumes")
        st.markdown("Upload multiple resume files to process them all at once")
        
        uploaded_files = st.file_uploader(
            "Choose resume files",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            help="Select multiple resume files to process"
        )
        
        if uploaded_files:
            st.info(f"📦 {len(uploaded_files)} file(s) selected")
            
            if st.button("🚀 Process All Resumes", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                all_results = []
                
                try:
                    parser = ResumeParser(api_key)
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
                        
                        # Create temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_path = tmp_file.name
                        
                        try:
                            result = parser.parse_from_file(tmp_path)
                            all_results.append({
                                "filename": uploaded_file.name,
                                "success": True,
                                "data": result
                            })
                        
                        except Exception as e:
                            all_results.append({
                                "filename": uploaded_file.name,
                                "success": False,
                                "error": str(e)
                            })
                        
                        finally:
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.success(f"✅ Completed processing {len(uploaded_files)} resume(s)")
                    
                    # Display results summary
                    with results_container:
                        st.subheader("📊 Batch Processing Results")
                        
                        success_count = sum(1 for r in all_results if r['success'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Processed", len(all_results))
                        with col2:
                            st.metric("Successful", success_count, delta=f"{(success_count/len(all_results)*100):.0f}%")
                        with col3:
                            st.metric("Failed", len(all_results) - success_count)
                        
                        st.divider()
                        
                        # Show individual results
                        for result in all_results:
                            with st.expander(f"📄 {result['filename']}"):
                                if result['success']:
                                    st.json(result['data'])
                                    
                                    # Download option for individual result
                                    json_str = json.dumps(result['data'], indent=2)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_str,
                                        file_name=f"{Path(result['filename']).stem}_parsed.json",
                                        mime="application/json",
                                        key=f"download_{result['filename']}"
                                    )
                                else:
                                    st.error(f"❌ Error: {result['error']}")
                        
                        # Download all results
                        st.divider()
                        json_str = json.dumps(all_results, indent=2)
                        st.download_button(
                            label="⬇️ Download All Results as JSON",
                            data=json_str,
                            file_name="batch_results.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                except Exception as e:
                    st.error(f"❌ Batch processing error: {str(e)}")


if __name__ == "__main__":
    main()
