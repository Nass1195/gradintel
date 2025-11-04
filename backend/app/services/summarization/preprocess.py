from pathlib import Path
import pypdf
import re

from docx import Document


def read_file(file_path: Path) -> str:
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

def remove_Url(text: str) -> str:
    return re.sub(r'https?:\S*', '', text)


def remove_extra_spaces(text):
    return ' '.join(text.split())


def clean_text(text: str) -> str:
    lowercase_text = text.lower()
    no_url_text = remove_Url(lowercase_text)
    cleaned_text = remove_extra_spaces(no_url_text)
    return cleaned_text

   

def preprocess_input(file_path: Path) -> str:
    raw_text = read_file(file_path)
    cleaned_text = clean_text(raw_text)
    return cleaned_text
