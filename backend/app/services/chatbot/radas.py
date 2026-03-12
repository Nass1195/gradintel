import json
import re
from typing import Any

from app.services import llmModel
from app.services.chatbot.chatbot import generate_chat_response_with_context


async def evaluate_radas() -> dict[str, Any]:
   return {
        "radas_score": 0.85,
        "radas_explanation": "The answer is mostly relevant and accurate, but some information is missing. The retrieved chunks provided useful context, but the rewritten query could be more focused.",
    }
