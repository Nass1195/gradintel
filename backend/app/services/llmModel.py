from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama"
)

async def generate_text(messages, max_length=512):
    response = await client.chat.completions.create(
        model="qwen3:8b",
        messages=messages,
    )
    return response.choices[0].message.content


async def generate_embedding(input):
    response = await client.embeddings.create(
        model="embeddinggemma",
        input=input,
    )
    return [d.embedding for d in response.data]

