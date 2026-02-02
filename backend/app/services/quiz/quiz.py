from app.services.preprocess import preprocess
from app.services import llmModel

async def generate_quiz(file):
    preprocessed = await preprocess.preprocess_input(file)
    clean_text = preprocessed["clean_text"]
    
    quiz_questions = await generate_quiz_questions(clean_text, num_questions=5)
    
    return quiz_questions




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
    print("Quiz Generation Responses:", responses)
    return responses