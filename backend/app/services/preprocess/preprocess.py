from pathlib import Path
import pypdf
import re
import contractions
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import nltk
from fastapi import UploadFile
import io

from docx import Document


nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words('english'))

async def read_file(file: UploadFile) -> str:
    # Accept either a Path or a string path
    file_name = file.filename
    print(f"Reading file: {file_name}")
    ext = Path(file_name).suffix.lower()
    file_bytes = await file.read()
    if ext == '.txt':
        return read_txt(file_bytes)
    elif ext == '.pdf':
        return read_pdf(file_bytes)
    elif ext in ['.docx', '.doc']:
        return read_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def read_txt(file_bytes: bytes) -> str:
   return file_bytes.decode('utf-8')
    

def read_pdf(file_bytes: bytes) -> str:
    text = ""
    with io.BytesIO(file_bytes) as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file_bytes: bytes) -> str:
    text = ""
    with io.BytesIO(file_bytes) as f:
        doc = Document(f)
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

def normalize_text(text):
    return contractions.fix(text)

def tokenize_text(text):
    return word_tokenize(text)

def remove_stopwords(tokens):
    return [word for word in tokens if word not in stop_words]

def lemmatize_text(text):
    tagged = pos_tag(text)
    lemmatized = [
        lemmatizer.lemmatize(word, get_wordnet_pos(pos)) 
        for word, pos in tagged
    ]
    return lemmatized


def get_wordnet_pos(tag):
    """
    Convert POS tag from NLTK to WordNet compatible tag.
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # default

def split_sentences(text):
    return nltk.sent_tokenize(text)

def chunk_text(sentences, max_len=2000):
    chunks, chunk = [], []
    length = 0
    for sent in sentences:
        length += len(sent.split())
        if length > max_len:
            chunks.append(' '.join(chunk))
            chunk, length = [sent], len(sent.split())
        else:
            chunk.append(sent)
    if chunk:
        chunks.append(' '.join(chunk))
    return chunks

def preprocess_text(text):
    text = clean_text(text)
    text = normalize_text(text)
    sentences = split_sentences(text)
    chunks = chunk_text(sentences)
    tokens = tokenize_text(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize_text(tokens)
    return {
        "clean_text": text,
        "sentences": sentences,
        "tokens": tokens,
        "chunks": chunks
    }

async def preprocess_input(file: UploadFile):
    raw_text = await read_file(file)
    processed_data = preprocess_text(raw_text)
    return processed_data
