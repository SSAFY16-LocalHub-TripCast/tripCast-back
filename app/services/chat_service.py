from app.services.embedding_service import search_context
from app.services.ai_service import ask_ai


def chat(user_message: str) -> str:
    context = search_context(user_message)
    response = ask_ai(user_message, context)
    return response