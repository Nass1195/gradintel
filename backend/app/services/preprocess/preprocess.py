from pathlib import Path
import pypdf
import re
from fastapi import UploadFile
import io

from docx import Document
from app.services.llmModel import generate_embedding
from app.models import ChunkCreate, Chunk
from uuid import UUID


BATCH_SIZE = 32



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



def chunk_text(text, max_len=2000, overlap=250):
    chunks = []
    chunk_index = 0
    n = len(text)
    start = 0
    while start < n:
        end = min(start + max_len, n)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)
            chunk_index += 1

        if end == n:
            break

        start = max( 0, end - overlap) 
    
    return chunks
        
def preprocess_text(text):
    text = clean_text(text)
    chunks = chunk_text(text)
    return {
        "clean_text": text,
        "chunks": chunks
    }

async def preprocess_input(file: UploadFile):
    raw_text = await read_file(file)
    processed_data = preprocess_text(raw_text)
    return processed_data


async def preprocess_text_for_chat(file: UploadFile, document_id: UUID, session):
    processed_data = await preprocess_input(file)
    chunks = processed_data["chunks"]
    embeddings = await embed_chunks(chunks)
    store_chunks(chunks, embeddings, document_id, session)




async def embed_chunks(chunks: list[str]):
    embeddings = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]
        batch_embeddings = await generate_embedding(batch)
        embeddings.extend(batch_embeddings)
    return embeddings


def store_chunks(chunks: list[str], embeddings: list[list[float]], document_id: UUID, session):
    chunks_to_store = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_obj = ChunkCreate(
            content=chunk,
            chunk_index=i,
            embedding=embedding,
        )
        db_chunk = Chunk.model_validate(chunk_obj, update={"document_id": document_id})
        chunks_to_store.append(db_chunk)
    
    session.add_all(chunks_to_store)
    session.commit()
        