from pydantic import ValidationError

from app.core.config import settings
from app.services.quiz.quiz import generate_quiz
from app.services.llmModel import generate_text
from app.api.deps import SessionDep
from app.models import QuizQuestion, MCQEvaluation


async def evaluate_quiz(session: SessionDep) -> list[MCQEvaluation]:

    quiz, chunks_content = await generate_quiz(settings.TEST_ITEM, session)

    evaluations: list[MCQEvaluation] = []

    for i, chunk_content in enumerate(chunks_content):
        eval1 = await evaluate_mcq_quality(chunk_content, quiz[2*i])
        eval2 = await evaluate_mcq_quality(chunk_content, quiz[2*i + 1])
        evaluations.append(eval1)
        evaluations.append(eval2)

    print(evaluations)
    valid_quiz_evals = [q for q in evaluations if isinstance(q, MCQEvaluation)]

    return valid_quiz_evals


async def evaluate_mcq_quality(source_text: str, mcq_data: QuizQuestion) -> MCQEvaluation:
    system_instruction = """
    You are an expert educational assessor. Your task is to evaluate a Multiple Choice Question (MCQ) 
    that was generated based on a specific source text.

    EVALUATION CRITERIA:
    Score the following out of 5 (1 = Very Poor, 5 = Excellent):
    1. Accuracy (1-5): Is the correct answer factually correct according to the text?
    2. Clarity (1-5): Is the question clear, unambiguous, and grammatically correct?
    3. Distractor Quality (1-5): Are the incorrect options plausible but definitively wrong?

    Respond ONLY with a valid JSON object in the exact format below. Do not add markdown blocks or other text.
    {
        "accuracy_score": <int>,
        "clarity_score": <int>,
        "distractor_score": <int>,
        "total_score": <int>,
        "reasoning": "<A brief 2-sentence explanation of the scores>"
    }
    """.strip()

    evaluation_prompt = f"""
    SOURCE TEXT:
    "{source_text}"

    GENERATED MCQ:
    Question: {mcq_data.question}
    Options: {', '.join(mcq_data.options)}
    Correct Answer: {mcq_data.correct_answer}
    """.strip()

    try:

        raw_response = await generate_text([
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": evaluation_prompt}
        ])

        cleaned_response = raw_response.replace("```json", "").replace("```", "").strip()

        evaluation_result = MCQEvaluation.model_validate_json(cleaned_response)

        return evaluation_result
    except ValidationError as e:
        return {"error": "LLM returned invalid data types or missing fields.", "details": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}