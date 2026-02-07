from openai import AsyncOpenAI

cleint = AsyncOpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama"
)

async def generate_text(messages, max_length=512):
    response = await cleint.chat.completions.create(
        model="qwen2.5:3b",
        messages=messages,
        max_tokens=max_length,
    )
    return response.choices[0].message.content

