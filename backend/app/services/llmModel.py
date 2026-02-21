from openai import AsyncOpenAI

cleint = AsyncOpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama"
)

async def generate_text(messages, max_length=512):
    response = await cleint.chat.completions.create(
        model="gemma3:4b",
        messages=messages,
        max_tokens=max_length,
    )
    return response.choices[0].message.content


async def generate_embedding(input):
    response = await cleint.embeddings.create(
        model="embeddinggemma",
        input=input,
    )
    return [d.embedding for d in response.data]

