from app.services import llmModel
import json
from pydantic import BaseModel



class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_answer: str

class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    
async def generate_quiz(text):
    
    
    quiz_questions = await generate_quiz_questions(text, num_questions=5)

    try: 
        quiz_response = QuizResponse(questions=quiz_questions)
        for q in quiz_response.questions:
            print(f"Question ID: {q.id}")
            print(f"Question: {q.question}")
            print(f"Options: {q.options}")
            print(f"Correct Answer: {q.correct_answer}")
            print("-----")
    except Exception as e:
        print("Error parsing quiz questions:", e)
        quiz_response = QuizResponse(questions=[])
    
    return quiz_response




async def generate_quiz_questions(text, num_questions=5):

    system_instruction = """
        You are a helpful assistant that generates multiple-choice quizzes.
        You must return the output as a valid JSON array of objects. 
        Do not include markdown formatting (like ```json).

        Follow this JSON schema exactly:
        [
        {
            "id": 1,
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

    try:
        quiz_data = json.loads(responses)
    except json.JSONDecodeError:
        print("Raw output:", responses)
    print("Quiz Generation Responses:", quiz_data)
    return quiz_data