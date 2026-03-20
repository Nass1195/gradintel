from sqlmodel import select, delete
from typing import Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Item,
    Message,
    Document,
    DocumentCreate,
    DocumentsPublic,
    UploadResponse,
    ChatMessageCreate,
    ChatMessage,
    ChatMessagesPublic,
    QuizPublic,
    QuizQuestion,
    RadasEvaluationPublic,
    Chunk,
)
from app.services.preprocess import preprocess
from app.services.summarization import summary as summarization_model
from app.services.quiz import quiz as quiz_model
from app.services.chatbot import chatbot 
from app.services.eval import RAG_eval

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.post("/chat/{item_id}", response_model=Message)
async def chat_with_document(
     *, item_id: UUID, session: SessionDep, current_user: CurrentUser, user_input: Message
) -> Message:
     
     item = session.get(Item, item_id)
     if not item:
          raise HTTPException(status_code=404, detail="Item not found")
     if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
     user_message = ChatMessageCreate(message=user_input.message, role="user")
     db_message = ChatMessage.model_validate(user_message, update={"owner_id": item_id})

     session.add(db_message)
     session.commit()
     session.refresh(db_message)

     response, _ = await chatbot.generate_chat_response(user_input.message, item_id, session)

     assistant_message = ChatMessageCreate(message=response, role="assistant")
     db_assistant_message = ChatMessage.model_validate(assistant_message, update={"owner_id": item_id})

     session.add(db_assistant_message)
     session.commit()
     session.refresh(db_assistant_message)

     return Message(message=response)


@router.get("/chat/evaluate", response_model=RadasEvaluationPublic)
async def evaluate_chatbot_radas(
    *, session: SessionDep, current_user: CurrentUser
) -> RadasEvaluationPublic:
     if not current_user.is_superuser:
          raise HTTPException(status_code=400, detail="Not enough permissions")
     
     evaluation = await RAG_eval.evaluate_RAG(session)
     return RadasEvaluationPublic.model_validate(evaluation)


@router.get("/chat/{item_id}", response_model=ChatMessagesPublic)
def get_chat_history(
     *, item_id: UUID, session: SessionDep, current_user: CurrentUser
) -> ChatMessagesPublic:
     
     statement = select(ChatMessage).where(ChatMessage.owner_id == item_id).order_by(ChatMessage.created_at)
     messages = session.exec(statement).all()

     if not current_user.is_superuser and ( messages and (messages[0].owner.owner_id != current_user.id)):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
     return ChatMessagesPublic(data=messages)




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

     summary = await summarization_model.summarize_file(chunks)

     document = DocumentCreate(title=file.filename, content=text, summary=summary)
     db_document = Document.model_validate(document, update={"owner_id": item_id})

     session.add(db_document)
     session.commit()
     session.refresh(db_document)
     
     await preprocess.preprocess_text_for_chat(chunks, db_document.id, session)

     item_summary = await summarization_model.generate_item_summry(item_id, session)

     return UploadResponse( document=db_document, summary=item_summary)





@router.delete("/{id}")
def delete_document(
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
     summary = summarization_model.generate_item_summry(item_id, session)
     return Message(message=summary or "No summary available.")





@router.get("/quiz/generate/{item_id}", response_model=QuizPublic)
async def generate_quiz_endpoint(
     *, session: SessionDep, current_user: CurrentUser, item_id: UUID
) -> QuizPublic:
     item = session.get(Item, item_id)
     if not item:
          raise HTTPException(status_code=404, detail="Item not found")
     if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
     print(f"Received file for quiz generation")
     quiz = await quiz_model.generate_quiz(item_id, session)
     print("Generated quiz")

     return QuizPublic(questions=quiz)

@router.get("/quiz/{id}", response_model=QuizPublic)
async def get_quiz_endpoint(
     *, session: SessionDep, current_user: CurrentUser, id: UUID
) -> QuizPublic:
     statement = select(QuizQuestion).where(QuizQuestion.item_id == id)
     quiz = session.exec(statement).all()

     if not quiz:
          raise HTTPException(status_code=404, detail="quiz not found")
     if not current_user.is_superuser and (quiz[0].item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     

     return QuizPublic(questions=quiz)

@router.post("/quiz/complete")
def update_chunks(
     *, session: SessionDep, current_user: CurrentUser, answered_quiz: QuizPublic
) -> Message:
     chunks: list[Chunk] = []
     chunk_ids = []

     for quiz in answered_quiz.questions:
          isCorrect = quiz.is_correct
          chunk_id = quiz.chunk_id

          if chunk_id in chunk_ids:
               for chunk in chunks:
                    if chunk.id == chunk_id:
                         chunk.num_answered_questions += 1
                         chunk.correct_answers += int(isCorrect)
          else:
               chunk = session.get(Chunk, chunk_id)
               
               if not chunk:
                    continue
               chunk.num_answered_questions += 1
               chunk.correct_answers += int(isCorrect)
               chunks.append(chunk)
               chunk_ids.append(chunk_id)

     if not chunks:
          raise HTTPException(status_code=404, detail="chunks not found")
     if not current_user.is_superuser and (chunks[0].document.owner.owner_id != current_user.id):
          raise HTTPException(status_code=400, detail="Not enough permissions")

     item_id = chunks[0].document.owner_id
     statement = delete(QuizQuestion).where(QuizQuestion.item_id == item_id)
     session.exec(statement)

     session.add_all(chunks)
     session.commit()

     return Message(message="answer received")

