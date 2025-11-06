from pathlib import Path
import pypdf
import re

from docx import Document


def read_file(file_path: Path) -> str:
    # Accept either a Path or a string path
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    if ext == '.txt':
        return read_txt(file_path)
    elif ext == '.pdf':
        return read_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return read_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def read_txt(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    

def read_pdf(file_path: Path) -> str:
    text = ""
    with open(file_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file_path: Path) -> str:
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'<[^>]+>', '', text)        # remove HTML tags
    text = re.sub(r'http\S+|www.\S+', '', text) # remove URLs
    text = re.sub(r'[^a-z0-9.,!?;:\'\"\s]', '', text) # keep basic punctuation
    text = re.sub(r'\s+', ' ', text).strip()   # remove extra spaces
    return text



def chunk_text(text, max_words=400, overlap=50):

    words = text.split()
    start = 0
    while start < len(words):
        end = start + max_words
        chunk = words[start:end]
        yield " ".join(chunk)
        start = end - overlap 

def preprocess_input(file_path: Path) -> str:
    raw_text = read_file(file_path)
    cleaned_text = clean_text(raw_text)
    return cleaned_text

