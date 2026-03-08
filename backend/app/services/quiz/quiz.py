from app.services import llmModel
import json
import re
from sqlmodel import select
from app.models import Document, QuizQuestionsCreate, Chunk, Item, QuizQuestion
from app.api.deps import SessionDep
import random
import math


def retrieve_text_from_db(item_id: str, session: SessionDep):
    statment =   (select(Chunk)
    .join(Chunk.document)
    .join(Document.owner)
    .where(Item.id == item_id)
    )
    documents_chuncks = session.exec(statment).all()
    if not documents_chuncks:
        raise ValueError("Document not found")
    return documents_chuncks

    
async def generate_quiz(item_id: str, session: SessionDep):
    
    documents_chuncks = retrieve_text_from_db(item_id, session)
    all_questions = []
    selected_chunks = select_chenks_for_quiz(documents_chuncks, num_chunks=5)
    for chunk in selected_chunks:
        quiz_questions = await generate_quiz_questions(chunk.content, num_questions=2)
        all_questions.extend(quiz_questions)
   

    try: 
        quiz_response = QuizQuestionsCreate(questions=all_questions)
        for q in quiz_response.questions:
            print(f"Question: {q.question}")
            print(f"Options: {q.options}")
            print(f"Correct Answer: {q.correct_answer}")
            print("-----")
    except Exception as e:
        print("Error parsing quiz questions:", e)
        quiz_response = QuizQuestionsCreate(questions=[])

    quiz_db = [QuizQuestion.model_validate(q, update={"item_id": item_id}) for q in quiz_response.questions]
    session.add_all(quiz_db)
    session.commit()
    for question in quiz_db:
        session.refresh(question) 
    
    return quiz_db



def clean_quiz_response(raw_response):
    clean_text = re.sub(r'```json', '', raw_response)
    clean_text = re.sub(r'```', '', clean_text)
    return clean_text.strip()
    
    

async def generate_quiz_questions(text, num_questions=5):

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
    print("Quiz Generation Responses:", quiz_data)
    return quiz_data


def select_chenks_for_quiz(chunks, num_chunks=5):
    total_chunks = len(chunks)
    if total_chunks <= num_chunks:
        return chunks
    
    selected_chunks = []

    step = total_chunks / num_chunks
    for i in range(num_chunks):
        start_idx = math.floor(i * step)
        end_idx  = math.floor((i + 1) * step) if i < num_chunks - 1 else total_chunks

        bucket = chunks[start_idx:end_idx]

        selected_chunk = random.choice(bucket)
        selected_chunks.append(selected_chunk)

    return selected_chunks