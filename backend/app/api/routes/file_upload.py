from sqlmodel import select
from typing import Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Document, DocumentCreate, DocumentPublic
from app.services.preprocess import preprocess
from app.services.summarization import model as summarization_model
from app.services.quiz import quiz as quiz_model

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.get("/{id}", response_model=DocumentPublic)
def read_document(id: UUID, session: SessionDep, current_user: CurrentUser) -> Any:
   
     statment = select(Document).where(Document.owner_id == id)
     document = session.exec(statment).one_or_none()
     if not document:
        raise HTTPException(status_code=404, detail="Document not found")
     
     return document

@router.post("/{item_id}", response_model=Message)
async def upload_file(
     *,item_id: UUID , session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Message:
     print(f"Received file: {file.filename}")
     text = await preprocess.read_file(file)
     file.file.seek(0)
     summary = await summarization_model.summarize(file)
     document = DocumentCreate(title=file.filename, content=text, summary=summary)
     db_document = Document.model_validate(document, update={"owner_id": item_id})
     session.add(db_document)
     session.commit()
     session.refresh(db_document)
     return Message(message=summary)


@router.post("/quiz", response_model=quiz_model.QuizResponse)
async def generate_quiz_endpoint(
     *, session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> quiz_model.QuizResponse:
     print(f"Received file for quiz generation: {file.filename}")
     quiz = await quiz_model.generate_quiz(file)
     return quiz