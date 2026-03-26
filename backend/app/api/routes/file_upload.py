from sqlmodel import select
from typing import Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Item,
    Message,
    Document,
    DocumentCreate,
    DocumentsPublic,
    UploadResponse,
)
from app.services.preprocess import preprocess
from app.services.summarization import summary as summarization_model

router = APIRouter(prefix="/upload", tags=["file_upload"])


@router.get("/{id}", response_model=DocumentsPublic)
def read_document(id: UUID, session: SessionDep, current_user: CurrentUser) -> Any:
   
     statment = select(Document).where(Document.owner_id == id)
     documents = session.exec(statment).all()
     if not documents:
          raise HTTPException(status_code=404, detail="Document not found")
     if not current_user.is_superuser and (documents[0].owner.owner_id != current_user.id):
          raise HTTPException(status_code=400, detail="Not enough permissions")
     
     return DocumentsPublic(data=documents)


@router.post("/{item_id}", response_model=UploadResponse)
async def upload_file(
     *,item_id: UUID , session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Any:  
     item = session.get(Item, item_id)
     if not item:
          raise HTTPException(status_code=404, detail="Item not found")
     if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
     preprocessed = await preprocess.preprocess_input(file)
     chunks = preprocessed["chunks"]
     text = preprocessed["clean_text"]

     summary = await summarization_model.summarize_file(text)

     document = DocumentCreate(title=file.filename, content=text, summary=summary)
     db_document = Document.model_validate(document, update={"owner_id": item_id})

     session.add(db_document)
     session.commit()
     session.refresh(db_document)
     
     await preprocess.preprocess_text_for_chat(chunks, db_document.id, session)

     item_summary = await summarization_model.generate_item_summary(item_id, session)

     return UploadResponse( document=db_document, summary=item_summary)



@router.delete("/{id}")
async def delete_document(
    session: SessionDep, current_user: CurrentUser, id: UUID
) -> Message:
     document = session.get(Document, id)
     if not document:
          raise HTTPException(status_code=404, detail="Document not found")
     if not current_user.is_superuser and (document.owner.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
     item_id = document.owner_id
     session.delete(document)
     session.commit()
     summary = await summarization_model.generate_item_summary(item_id, session)
     return Message(message=summary or "No summary available.")


