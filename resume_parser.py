"""
Resume Parser using Google Gemini API
Extracts structured information from resume text
"""

import json
import time
import hashlib
import os
from pathlib import Path
import re

try:
    import google.generativeai as genai
except ImportError:
    genai = None

import PyPDF2
from docx import Document


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")


def get_file_text(file_path):
    """Extract text from various file formats"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_path)
    elif file_ext in ['.txt', '.text']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def get_cache_key(resume_text):
    """Generate cache key from resume text"""
    return hashlib.md5(resume_text.encode()).hexdigest()


class ResumeParser:
    """Parse resumes using Gemini API"""
    
    def __init__(self, api_key, cache_dir='cache', use_cache=True):
        """
        Initialize the parser
        
        Args:
            api_key: Google Gemini API key
            cache_dir: Directory to store cached results
            use_cache: Whether to use caching
        """
        if not api_key:
            raise ValueError("API key is required")
            
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        
        if use_cache:
            os.makedirs(cache_dir, exist_ok=True)
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _get_prompt(self, resume_text):
        """Generate the prompt for Gemini"""
        return """You are an expert resume parser. Extract the following information from the resume and respond ONLY with valid JSON, no markdown formatting:

{
  "name": "Full name",
  "phone": "Phone number or null if not found",
  "email": "Email address or null if not found",
  "position": "Current or most recent job position/title or null if not found",
  "summary": "Brief professional summary (2-3 sentences) or null",
  "primarySkills": ["List of 5-8 core technical skills"],
  "secondarySkills": ["List of additional supporting skills"],
  "experience": "Years of professional experience or null",
  "education": "Highest education qualification or null",
  "skillsSource": "Brief explanation of how skills were determined"
}

Instructions:
1. Extract name, phone, email, and position directly from the resume
2. Identify primary skills as core technical competencies mentioned most frequently
3. Identify secondary skills as supporting technologies and tools
4. If skills aren't explicitly listed, infer from projects, work experience, and education
5. Return ONLY valid JSON with no markdown backticks, no preamble, no explanation
6. Use null for any field that cannot be determined
7. Ensure all arrays and strings are properly quoted

Resume:
""" + resume_text
    
    def _clean_json_response(self, text):
        """Clean API response to valid JSON"""
        # Remove markdown code blocks if present
        text = text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        text = text.strip()
        
        # Try to find JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        
        return text
    
    def parse_resume(self, resume_text, max_retries=3):
        """
        Parse resume and extract structured data
        
        Args:
            resume_text: Text content of resume
            max_retries: Number of retries on failure
            
        Returns:
            dict: Parsed resume data
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty")
        
        # Check cache
        if self.use_cache:
            cache_key = get_cache_key(resume_text)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        # Call Gemini API with retries
        for attempt in range(max_retries):
            try:
                prompt = self._get_prompt(resume_text)
                
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.1,
                        'max_output_tokens': 2000,
                    }
                )
                
                if not response.text:
                    raise ValueError("Empty response from API")
                
                # Clean and parse response
                cleaned_text = self._clean_json_response(response.text)
                result = json.loads(cleaned_text)
                
                # Cache result
                if self.use_cache:
                    cache_key = get_cache_key(resume_text)
                    cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
                    with open(cache_file, 'w') as f:
                        json.dump(result, f, indent=2)
                
                return result
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise Exception(f"Failed to parse JSON response after {max_retries} attempts: {str(e)}")
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise e
        
        raise Exception("Failed to parse resume after all retries")
    
    def parse_from_file(self, file_path):
        """Parse resume from file (PDF, DOCX, or TXT)"""
        resume_text = get_file_text(file_path)
        return self.parse_resume(resume_text)


def batch_parse_resumes(resume_folder, api_key, output_file="results.json"):
    """
    Parse multiple resumes in a folder
    
    Args:
        resume_folder: Path to folder containing resumes
        api_key: Google Gemini API key
        output_file: Where to save results
        
    Returns:
        list: List of parsing results
    """
    parser = ResumeParser(api_key)
    results = []
    
    resume_files = list(Path(resume_folder).glob('*.txt')) + \
                   list(Path(resume_folder).glob('*.pdf')) + \
                   list(Path(resume_folder).glob('*.docx'))
    
    for i, resume_path in enumerate(resume_files):
        print(f"Processing {i+1}/{len(resume_files)}: {resume_path.name}")
        
        try:
            parsed_data = parser.parse_from_file(str(resume_path))
            
            results.append({
                "filename": resume_path.name,
                "success": True,
                "data": parsed_data
            })
            
        except Exception as e:
            results.append({
                "filename": resume_path.name,
                "success": False,
                "error": str(e)
            })
        
        # Rate limiting
        if i < len(resume_files) - 1:
            time.sleep(1)
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    return results
