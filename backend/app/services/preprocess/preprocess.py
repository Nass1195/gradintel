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



def chunk_text(text, max_len=2000, overlap=250, separators=None):

    if separators is None:
        separators = ["\n\n", "\n", ".", " ", ""]

    if len(text) <= max_len:
        return [text]
    
    active_separator = separators[-1]
    next_separators = []

    for i, sep in enumerate(separators):
        if sep == "" or sep in text:
            active_separator = sep
            next_separators = separators[i+1:]
            break

    if active_separator != "":
        splits = text.split(active_separator)
    else:
        splits = list(text)


    good_splits = []
    for split in splits:
        if len(split) < max_len:
            good_splits.append(split)
        else:
            good_splits.extend(chunk_text(split, max_len, overlap, next_separators))
    
    final_chunks = []
    current_chunk = []
    current_length = 0

    for split in good_splits:
        sep_length = len(active_separator) if current_chunk else 0
        split_length = len(split)
        if current_length + split_length + sep_length <= max_len:
            current_chunk.append(split)
            current_length += split_length + sep_length
        else:
            final_chunks.append(active_separator.join(current_chunk))
            while current_length > overlap or (current_length + split_length > max_len and current_chunk):
                removed = current_chunk.pop(0)
                current_length -= len(removed) + (len(active_separator) if current_chunk else 0)

            current_chunk.append(split)
            current_length += split_length + (len(active_separator) if current_chunk else 0)

    if current_chunk:
        final_chunks.append(active_separator.join(current_chunk))
   
    
    return final_chunks
        
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


async def preprocess_text_for_chat(chunks: list[str], document_id: UUID, session):
    
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
        