from app.services import llmModel
import json
import re
from sqlmodel import select, delete
from app.models import Document, QuizQuestionsCreate, Chunk, Item, QuizQuestion
from app.api.deps import SessionDep
import random
import math


def retrieve_text_from_db(item_id: str, session: SessionDep) -> list[Chunk]:
    statement =   (select(Chunk)
    .join(Chunk.document)
    .join(Document.owner)
    .where(Item.id == item_id)
    )
    documents_chuncks = session.exec(statement).all()
    if not documents_chuncks:
        raise ValueError("Document not found")
    return documents_chuncks

def get_struggled_chunks(item_id: str, session: SessionDep, accept_ratio: float) -> list[Chunk]:
    statement =   (select(Chunk)
    .join(Chunk.document)
    .where(Document.owner_id == item_id, Chunk.num_answered_questions > 0, Chunk.correct_answers <= (accept_ratio * Chunk.num_answered_questions))
    )
    wrong_questions = session.exec(statement).all()

    return wrong_questions

    
async def generate_quiz(item_id: str, session: SessionDep):
    
    all_questions = []
    chunk_ids = []
    selected_chunks = select_chenks_for_quiz(item_id, session, num_chunks=5)
    for chunk in selected_chunks:
        quiz_questions = await generate_quiz_questions(chunk.content, num_questions=2)
        all_questions.extend(quiz_questions)
        if quiz_questions:
            chunk_ids.append(chunk.id)
        
    
    statement = delete(QuizQuestion).where(QuizQuestion.item_id == item_id)
    session.exec(statement)
    session.commit()


    quiz_db = []
    for i, chunk_id in enumerate(chunk_ids):
        q1 = all_questions[2*i]
        q2 = all_questions[2*i + 1]
        quiz_db.append(QuizQuestion.model_validate(q1, update={"item_id": item_id, "chunk_id": chunk_id}))
        quiz_db.append(QuizQuestion.model_validate(q2, update={"item_id": item_id, "chunk_id": chunk_id}))

    session.add_all(quiz_db)
    session.commit()
    for question in quiz_db:
        session.refresh(question) 
    
    return quiz_db

def clean_quiz_response(raw_response: str) -> str:
    clean_text = re.sub(r'```json', '', raw_response)
    clean_text = re.sub(r'```', '', clean_text)
    return clean_text.strip()
    

async def generate_quiz_questions(text: str, num_questions=5):

    system_instruction = """
        You are a helpful assistant that generates multiple-choice quizzes.
        You must return the output as a valid JSON array of objects. 
        Do not include markdown formatting (like ```json).

        Follow this JSON schema exactly:
        [
            {
                "question": "The question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A"
                "explanation": "explain the answer"
            }
        ]
    """

    user_prompt = f"""
        Generate {num_questions} multiple-choice questions based on the following text. 
        Ensure the questions cover the most important concepts.

        TEXT:
        {text}
    """
    
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]
    
    responses = await llmModel.generate_text(messages, max_length=1024)
    cleaned_response = clean_quiz_response(responses)

    try:
        quiz_data = json.loads(cleaned_response)
    except json.JSONDecodeError:
        print("Raw output:", cleaned_response)
        return []

    return quiz_data


def select_chenks_for_quiz( item_id: str, session: SessionDep, num_chunks=6) -> list[Chunk]:

    chunks = retrieve_text_from_db(item_id, session)

    total_chunks = len(chunks)

    if total_chunks <= num_chunks:
        return chunks
    
    item = session.get(Item, item_id)

    selected_chunks = []

    struggled_pool = get_struggled_chunks(item_id, session, item.accept_ration)
    print(len(struggled_pool))

    if len(struggled_pool) < math.ceil(num_chunks / 2):
        item.accept_ration = min(0.95, item.accept_ration + 0.05)
        session.add(item)
        session.commit()
    elif len(struggled_pool) > 2 * math.ceil(num_chunks / 2):
        item.accept_ration = max(0.0,  item.accept_ration - 0.05)
        session.add(item)
        session.commit()

    review_limit = min(len(struggled_pool), math.ceil(num_chunks / 2))

    if review_limit > 0:
        selected_review_chunks = random.sample(struggled_pool, review_limit)
        selected_chunks.extend(selected_review_chunks)

    remaining_slots = num_chunks - len(selected_chunks)
    if remaining_slots > 0:
        remaining_pool = [c for c in chunks if c not in selected_chunks]

        total_remaining = len(remaining_pool)

        if total_remaining <= remaining_slots:
            selected_chunks.extend(remaining_pool)
            return selected_chunks
        

        step = total_remaining / remaining_slots
        for i in range(remaining_slots):
            start_idx = math.floor(i * step)
            end_idx  = math.floor((i + 1) * step) if i < num_chunks - 1 else total_chunks

            bucket = remaining_pool[start_idx:end_idx]

            if bucket:
                selected_chunk = random.choice(bucket)
                selected_chunks.append(selected_chunk)

    return selected_chunks