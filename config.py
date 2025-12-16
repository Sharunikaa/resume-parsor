# Resume Parser - Configuration
# This file contains default configuration values

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Cache configuration
CACHE_DIR = os.getenv('CACHE_DIR', './cache')
USE_CACHE = os.getenv('USE_CACHE', 'true').lower() == 'true'

# API Configuration
API_REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Rate limiting
REQUESTS_PER_MINUTE = 60
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE

# Model configuration
MODEL_NAME = 'gemini-2.5-flash'
TEMPERATURE = 0.1
MAX_TOKENS = 2000

# Supported file types
SUPPORTED_FORMATS = ['.txt', '.pdf', '.docx', '.text']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
