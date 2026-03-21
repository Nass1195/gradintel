from sqlmodel import select, delete
from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    QuizPublic,
    Item,
    QuizQuestion,
    Message,
    Chunk
)
from uuid import UUID
from app.services.quiz import quiz as quiz_model


router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/generate/{item_id}", response_model=QuizPublic)
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

@router.get("/{id}", response_model=QuizPublic)
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

@router.post("/complete")
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
