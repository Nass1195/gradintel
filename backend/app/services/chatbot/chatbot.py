from app.services import llmModel


async def generate_chat_response(user_input: str) -> str:
    system_instruction = """
    You are a helpful assistant that provides concise and accurate answers to user questions.
    Always provide clear and direct responses based on the user's input.
    If you don't know the answer, say "I don't know" instead of making up information.
    """

    massages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_input}
    ]
    response = await llmModel.generate_text(massages, max_length=512)
    return response