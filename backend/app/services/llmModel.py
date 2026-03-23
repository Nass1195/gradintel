from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

async def generate_text(messages, max_length=512):
    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
    )
    return response.choices[0].message.content


async def generate_embedding(input):
    response = await client.embeddings.create(
        model="gemini-embedding-001",
        input=input,
    )
    return [d.embedding for d in response.data]

