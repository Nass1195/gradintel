from sqlmodel import Session

from app.models import Chunk, Document, Item


def create_document_with_chunk(db: Session, item: Item) -> tuple[Document, Chunk]:
    doc = Document(
        title="Test document",
        content="Document body for tests.",
        summary="Short summary.",
        owner_id=item.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    embedding = [0.0] * 768
    chunk = Chunk(
        content="chunk text",
        chunk_index=0,
        embedding=embedding,
        document_id=doc.id,
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return doc, chunk
