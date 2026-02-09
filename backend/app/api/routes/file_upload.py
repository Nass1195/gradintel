from sqlmodel import select
from typing import Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Document, DocumentCreate, DocumentPublic, DocumentsPublic
from app.services.preprocess import preprocess
from app.services.summarization import model as summarization_model
from app.services.quiz import quiz as quiz_model
from app.services.chatbot import chatbot 

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.post("/chat", response_model=Message)
async def chat_with_document(
     *, session: SessionDep, current_user: CurrentUser, user_input: Message
) -> Message:
     print(f"Received chat request for item_id: with user input: {user_input.message}")
     response = await chatbot.generate_chat_response(user_input.message)
     return Message(message=response)

@router.get("/{id}", response_model=DocumentsPublic)
def read_document(id: UUID, session: SessionDep, current_user: CurrentUser) -> Any:
   
     statment = select(Document).where(Document.owner_id == id)
     documents = session.exec(statment).all()
     if not documents:
        raise HTTPException(status_code=404, detail="Document not found")
     
     return DocumentsPublic(data=documents)

@router.post("/{item_id}", response_model=DocumentPublic)
async def upload_file(
     *,item_id: UUID , session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Any:
     print(f"Received file: {file.filename}")
     text = await preprocess.read_file(file)
     file.file.seek(0)
     summary = await summarization_model.summarize(file)
     document = DocumentCreate(title=file.filename, content=text, summary=summary)
     db_document = Document.model_validate(document, update={"owner_id": item_id})
     session.add(db_document)
     session.commit()
     session.refresh(db_document)
     return db_document


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: UUID
) -> Message:
     document = session.get(Document, id)
     if not document:
          raise HTTPException(status_code=404, detail="Document not found")
     session.delete(document)
     session.commit()
     return Message(message="Document deleted successfully")

@router.get("/quiz/{id}", response_model=quiz_model.QuizResponse)
async def generate_quiz_endpoint(
     *, session: SessionDep, current_user: CurrentUser, id: UUID
) -> quiz_model.QuizResponse:
     print(f"Received file for quiz generation")
     quiz = await quiz_model.generate_quiz(id, session)
     return quiz