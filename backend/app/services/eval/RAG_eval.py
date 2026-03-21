import json
import re
from typing import Any
from datasets import load_dataset
import numpy as np
from app.services import llmModel
from app.services.chatbot.chatbot import generate_chat_response_with_context, cosine_similarity, generate_chat_response
from app.services.preprocess.preprocess import embed_chunks, store_chunks
from app.models import Item, DocumentCreate, Document, User
from sqlmodel import select
from app.core.config import settings


async def add_test_chunks_to_datadase(session):
    item = session.exec(select(Item).where(Item.id == settings.TEST_ITEM)).first()
    if not item:
        user: User = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
        if not user:
            return
        item = Item(id=settings.TEST_ITEM, title="Test Item", owner_id=user.id)
        session.add(item)
        session.commit()
        session.refresh(item)
        print("item_added")
        document = DocumentCreate(title="test doc")
        db_document = Document.model_validate(document, update={"owner_id": item.id})
        session.add(db_document)
        session.commit()
        session.refresh(db_document)
        print("document_added")
        dataset = load_dataset("vibrantlabsai/fiqa","corpus")
        data = dataset["corpus"]
        chunks = []
        for doc in data:
            chunk = doc["doc"]
            chunks.append(chunk)
        embeded_chuncks = await embed_chunks(chunks)
        store_chunks(chunks, embeded_chuncks, db_document.id , session)
        print("chuncks added")




async def evaluate_RAG(session) -> list[dict[str, Any]]:
    await add_test_chunks_to_datadase(session)

    dataset = load_dataset("vibrantlabsai/fiqa","ragas_eval")

    baseline = dataset["baseline"]
    evaluations = []
    similarity_scores = []
  
    for data in baseline:
        question = data.get("question")
        ground_truth = data.get("answer")
        contexts = data.get("contexts")
        contexts_chunks = split_mashed_dataset(contexts[0])
        generated_anwser, retrived_chunks = await generate_chat_response(question, settings.TEST_ITEM, session)
        evaluation = await evaluate(generated_anwser, ground_truth)
        genration_evaluation = evaluate_genration(question, generated_anwser, retrived_chunks, ground_truth)
        evaluations.append(genration_evaluation)
        similarity_scores.append(evaluation)
        print(compare_string_arrays(retrived_chunks, contexts_chunks)['overlap_percentage'])

    print(f"Average Similarity Score: {np.mean(similarity_scores)}")
   
    return evaluations

async def evaluate(answer, ground_truth):
    embeddings = await llmModel.generate_embedding([answer, ground_truth])
    answer_embedding = np.array(embeddings[0], dtype=np.float32)
    ground_truth_embedding = np.array(embeddings[1], dtype=np.float32)
    similarity_score = cosine_similarity(answer_embedding, ground_truth_embedding)
    print(f"Similarity Score: {similarity_score}")
    return similarity_score



async def evaluate_genration(question: str, answer: str, relevant_chunks: list[str], ground_truth: str ) -> dict[str, Any]:

    system_instruction = """You are an assistant that evaluates the quality of answers based on based on the following criteria:
    1. Relevance: Does the answer directly address the user's question?
    2. Accuracy: Is the information in the answer correct based on the relevant chunks and the Ground Truth provided?
    3. Completeness: Does the answer cover all key points mentioned in the Ground Truth?

        return the evaluation in the following JSON format:
        {
            "relevance_score": float,
            "accuracy_score": float,
            "completeness_score": float,
            "overall_score": float,
            "explanation": str
        }
    """.strip()


    evaluation_prompt = f"""
    Question: {question}
    generated Answer: {answer}
    Ground Truth: {ground_truth}
    Relevant Chunks: {relevant_chunks}

    Evaluate the quality of the answer based on relevance, accuracy, and completeness. Provide a score between 0 and 1, and a brief explanation for the score.
    """.strip()

    evaluation_response = await llmModel.generate_text(
        [{"role": "system", "content": system_instruction},
         {"role": "user", "content": evaluation_prompt}]
    )

    try:
        evaluation_data = json.loads(evaluation_response)
        return evaluation_data
    except json.JSONDecodeError:
        return {
            "score": 0.0,
            "explanation": "Failed to parse evaluation response.",
        }
    
def compare_string_arrays(retrieved_array: list[str], truth_array: list[str]) -> dict:
    
    set1 = set(retrieved_array)
    set2 = set(truth_array)
    
    return {
        "common_elements": list(set1.intersection(set2)),      
        "missing_from_truth": list(set2.difference(set1)),   
        "overlap_percentage": len(set1.intersection(set2)) / len(set2) if set2 else 0.0
    }


def split_mashed_dataset(mashed_string: str) -> list[str]:
    text = mashed_string.replace(r"\'", "'")
    fixed_string = re.sub(r'(?<=[a-z.!?])\"(?=[A-Z])', '|||"', text)
    fixed_string = re.sub(r'(?<=[a-z.!?])\\\"(?=[A-Z])', '|||"', fixed_string)

    clean_list = fixed_string.split('|||')
    
    return clean_list

