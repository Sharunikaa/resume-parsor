# 📄 Resume Parser with NLP

A sophisticated resume parsing application built with **spaCy NLP** and **Streamlit**. Extract structured information from resumes including personal details, skills, experience, and more. **No API key required. Completely offline. Free.**

## ✨ Features

- **🤖 NLP-Powered Parsing**: Uses spaCy entity recognition and regex patterns
- **📤 Multiple Format Support**: Process TXT, PDF, and DOCX files
- **🎯 Skill Extraction**: Identifies primary and secondary skills with 60+ keywords
- **💾 Smart Caching**: Avoids duplicate processing for the same resume
- **🚀 Batch Processing**: Process multiple resumes simultaneously
- **📥 Export Options**: Download results as JSON or Markdown
- **🎨 User-Friendly Interface**: Clean, intuitive Streamlit web application
- **⚡ Fast & Offline**: No API calls needed, instant processing
- **🔒 Privacy**: All data stays on your local machine
- **💰 Free**: $0 cost, no rate limits

## 📋 What Gets Extracted

- **Personal Details**: Name, Email, Phone Number
- **Professional Info**: Current Position, Years of Experience, Education
- **Skills**: Primary skills (core competencies) & Secondary skills (supporting)
- **Professional Summary**: AI-generated brief overview
- **Skill Attribution**: How skills were determined (explicit vs. inferred)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free at [makersuite.google.com](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory**
```bash
cd resume_extarctor
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📖 Usage Guide

### Option 1: Upload Resume File
1. Navigate to the "Upload Resume" tab
2. Upload a TXT, PDF, or DOCX file
3. Click "Parse Resume"
4. View and download results

### Option 2: Paste Text Directly
1. Go to the "Paste Text" tab
2. Paste your resume content
3. Click "Parse Resume"
4. Results appear immediately

### Option 3: Batch Processing
1. Select the "Batch Process" tab
2. Upload multiple resume files
3. Click "Process All Resumes"
4. View individual results or download all as JSON

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Your Gemini API Key
GEMINI_API_KEY=your_api_key_here

# Optional: Cache directory (default: ./cache)
CACHE_DIR=./cache

# Optional: Enable/disable caching (default: true)
USE_CACHE=true
```

### Config File

Edit `config.py` to customize:
- Model parameters (temperature, max tokens)
- Rate limiting settings
- Supported file formats
- Maximum file size
- Retry settings

## 📂 Project Structure

```
resume_extarctor/
├── app.py                 # Streamlit web application
├── resume_parser.py       # Core parsing logic and Gemini API integration
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment configuration
├── sample_resume.txt     # Sample resume for testing
└── README.md             # This file
```

## 🔑 Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the API key
5. Paste it into the app or add to `.env` file

**Free Tier**: 60 requests per minute (sufficient for most use cases)

## 💻 API Reference

### ResumeParser Class

```python
from resume_parser import ResumeParser

# Initialize parser
parser = ResumeParser(api_key="YOUR_API_KEY")

# Parse resume text
result = parser.parse_resume(resume_text)

# Parse from file (supports TXT, PDF, DOCX)
result = parser.parse_from_file("path/to/resume.pdf")

# Batch process multiple files
from resume_parser import batch_parse_resumes
results = batch_parse_resumes("folder_with_resumes/", api_key)
```

### Response Format

```json
{
  "name": "Sarah Johnson",
  "phone": "+1 (555) 123-4567",
  "email": "sarah.johnson@email.com",
  "position": "Senior Full Stack Developer",
  "summary": "Experienced developer with strong background in...",
  "primarySkills": ["React", "Node.js", "JavaScript", "TypeScript", "AWS", "Docker"],
  "secondarySkills": ["Redux", "Express.js", "PostgreSQL", "Kubernetes"],
  "experience": "7+ years",
  "education": "Bachelor of Science in Computer Science",
  "skillsSource": "Skills identified from explicit technical skills section and reinforced through project experience..."
}
```

## 🛠️ Advanced Usage

### Custom Parsing with Options

```python
# With caching disabled
parser = ResumeParser(api_key, use_cache=False)

# With custom cache directory
parser = ResumeParser(api_key, cache_dir='my_cache')

# Manual retry handling
result = parser.parse_resume(resume_text, max_retries=5)
```

### File Format Support

- **TXT**: Plain text files
- **PDF**: PDF documents (requires PyPDF2)
- **DOCX**: Microsoft Word documents (requires python-docx)

## ⚙️ Performance Optimization

### Caching
Results are cached by MD5 hash of resume text. Same resume won't be parsed twice:
```
cache/
├── a1b2c3d4e5f6g7h8i9j0.json
├── b2c3d4e5f6g7h8i9j0k1.json
└── ...
```

### Rate Limiting
Built-in rate limiter respects Gemini API quotas (60 req/min):
```python
# Automatic rate limiting
for resume in resumes:
    result = parser.parse_resume(resume)  # Automatically throttles
```

### Batch Processing
Process multiple resumes efficiently with automatic delays:
```python
results = batch_parse_resumes('resumes_folder/', api_key)
```

## 🐛 Troubleshooting

### Issue: "API key is invalid"
- Verify key format (should be 30+ characters)
- Check at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure no extra spaces in .env file

### Issue: "Empty response from API"
- Check resume text is not empty
- Try with sample_resume.txt first
- Verify API key has sufficient quota

### Issue: "JSON parsing errors"
- Ensure API response is valid JSON
- Check Streamlit logs for details
- Try increasing max_retries in configuration

### Issue: "Rate limit exceeded"
- Application has automatic rate limiting
- Default: 60 requests/minute (Gemini free tier)
- Adjust `REQUESTS_PER_MINUTE` in config.py

### Issue: "PDF/DOCX parsing fails"
- Ensure file is not corrupted
- Try converting to TXT or PDF
- Check file permissions

## 📊 Cost Analysis

**Gemini API Pricing** (Generous Free Tier):
- **Free tier**: 60 requests/minute, unlimited usage
- **1000 resumes**: Effectively $0 within free tier
- **Production scaling**: Pay-as-you-go when exceeding quotas

**Comparison**:
- GPT-4 API: ~$0.03 per resume
- GPT-3.5: ~$0.002 per resume
- **Gemini Pro: Effectively free for most use cases** ✨

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional file format support
- Enhanced skill categorization
- Export to additional formats (CSV, Excel)
- Database integration
- REST API endpoint

## 📝 License

This project is open source and available under the MIT License.

## 📚 Resources

- [Google Gemini API Documentation](https://ai.google.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python-DOCX Guide](https://python-docx.readthedocs.io/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)

## 🙋 Support

Having issues? Try these steps:
1. Check the Troubleshooting section above
2. Review Streamlit logs: `streamlit run app.py --logger.level=debug`
3. Test with sample_resume.txt first
4. Verify API key and internet connection

---

**Built with ❤️ using Google Gemini API and Streamlit**

Made to extract resume information efficiently and accurately.
