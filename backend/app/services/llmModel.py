from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

embedding_client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://host.docker.internal:11434/v1"
)

async def generate_text(messages, max_length=512):
    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
    )
    return response.choices[0].message.content


async def generate_embedding(input):
    response = await embedding_client.embeddings.create(
        model="embeddinggemma",
        input=input,
    )
    return [d.embedding for d in response.data]

