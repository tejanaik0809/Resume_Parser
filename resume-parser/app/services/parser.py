import os
import sys
import subprocess
import docx
import re
from app.utils.logger import logger

try:
    import pypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or DOCX file."""
    logger.info(f"Extracting text from: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == '.pdf':
            text = _extract_from_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            text = _extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only PDF and DOCX are supported.")
            
        # Clean text
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        
        logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise e

def _extract_from_pdf(file_path: str) -> str:
    reader = pypdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
    
def _extract_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
