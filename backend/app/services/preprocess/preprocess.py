from pathlib import Path
import pypdf
import re
import contractions
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import nltk


from docx import Document


nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words('english'))

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

def split_sentences(text):
    return nltk.sent_tokenize(text)

def chunk_text(sentences, max_len=512):
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

def preprocess_input(file_path: Path):
    raw_text = read_file(file_path)
    processed_data = preprocess_text(raw_text)
    return processed_data

print(normalize_text(clean_text("I'm testing the preprocessing module! Visit http://example.com for more info.")))