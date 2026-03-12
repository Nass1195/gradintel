from app.services import llmModel
from sqlmodel import select
from app.models import Document, Chunk, Item, ChatMessage
import numpy as np


async def generate_chat_response(user_input: str, item_id, session) -> str:
    response, _, _ = await generate_chat_response_with_context(user_input, item_id, session)
    return response


async def generate_chat_response_with_context(
    user_input: str, item_id, session
) -> tuple[str, list[str], str]:
    history_statement = (
        select(ChatMessage)
        .where(ChatMessage.owner_id == item_id)
        .order_by(ChatMessage.created_at)
    )
    history = session.exec(history_statement).all()
    history = history[-6:]
    rewritten_query = await add_context_to_query(user_input, history)
    relevant_chunks = await retrieve_relevant_information(rewritten_query, item_id, session)

    formatted_chunks = [f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(relevant_chunks)]
    context_text = "\n\n".join(formatted_chunks)

    system_instruction = """
    You are a retrieval-augmented assistant.

    RULES:
    - Answer ONLY using the provided CONTEXT.
    - Do NOT use outside knowledge.
    - If the answer is not in the context, say "I don't know."
    - When you use information, strictly cite sources using the provided labels, e.g., [Source 1], [Source 2].
    - Be concise and precise.
    """.strip()

    history_messages = []
    for message in history:
        role = "user" if message.role == "user" else "assistant"
        history_messages.append({"role": role, "content": message.message})

    user_prompt = f"""
    User's question:
    {user_input}
    Relevant information retrieved from documents:
    {context_text}
    Answer:
    """.strip()

    messages = [
        {"role": "system", "content": system_instruction},
        *history_messages,
        {"role": "user", "content": user_prompt},
    ]
    response = await llmModel.generate_text(messages, max_length=512)
    return response, relevant_chunks, rewritten_query

def cosine_similarity(vecA, vecB):
    dot_product = np.dot(vecA, vecB)
    normA = np.linalg.norm(vecA)
    normB = np.linalg.norm(vecB)
    if normA == 0 or normB == 0:
        return 0.0
    return dot_product / (normA * normB)

async def retrieve_relevant_information(user_input: str, item_id, session, k: int = 5) -> list[str]:
    query_embeddings = await llmModel.generate_embedding([user_input])
    embeddings = np.array(query_embeddings[0], dtype=np.float32)
    statment =   (select(Chunk)
    .join(Chunk.document)
    .join(Document.owner)
    .where(Item.id == item_id)
    )
    chunks = session.exec(statment).all()

    if not chunks:
        return [""]
    
    scores = []
    for chunk in chunks:
        if chunk.embedding is None:
            continue
        chunk_embedding = np.array(chunk.embedding, dtype=np.float32)
        score = cosine_similarity(embeddings, chunk_embedding)
        scores.append((score, chunk.content))

    scores.sort(key=lambda x: x[0], reverse=True)

    top_chunks = [content for _, content in scores[:k]]

    return top_chunks


async def add_context_to_query(user_input: str, history: list[ChatMessage]) -> str:

    conversation = ""
    for message in history:
        role = "User" if message.role == "user" else "Assistant"
        conversation += f"{role}: {message.message}\n"
    
    system_instruction = f"""
    You are a query-rewriting assistant for a RAG system.
    Task:
    Rewrite the user's latest message into a SINGLE standalone search query that can be used to retrieve relevant document chunks.
    Use the conversation context ONLY to resolve references (e.g., "it", "that", "the second one").
    Preserve any constraints and key entities (names, IDs, technical terms).
    Do NOT answer the question. Do NOT add new facts.
    Output ONLY the rewritten query, no quotes, no bullet points.
    """.strip()


    user_prompt = f"""
    Conversation history:
    {conversation}

    User's latest message:
    {user_input}

    Rewritten standalone query:
    """.strip()

    standalone_query = await llmModel.generate_text([{"role": "system", "content": system_instruction},
                                                     {"role": "user", "content": user_prompt}])
    
    return standalone_query
    