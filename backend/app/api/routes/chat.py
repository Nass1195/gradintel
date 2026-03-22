from fastapi import APIRouter, HTTPException
from app.models import (
    ChatMessage,
    Message,
    Item,
    ChatMessageCreate,
    ChatMessagesPublic,
    EvaluationPublic
)
from app.services.chatbot import chatbot
from uuid import UUID
from app.api.deps import CurrentUser, SessionDep
from sqlmodel import select
from app.services.eval import RAG_eval, summary_eval, quiz_eval



router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/{item_id}", response_model=Message)
async def chat_with_document(
    *, item_id: UUID, session: SessionDep, current_user: CurrentUser, user_input: Message
) -> Message:
     
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    user_message = ChatMessageCreate(message=user_input.message, role="user")
    db_message = ChatMessage.model_validate(user_message, update={"owner_id": item_id})

    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    response, _ = await chatbot.generate_chat_response(user_input.message, item_id, session)

    assistant_message = ChatMessageCreate(message=response, role="assistant")
    db_assistant_message = ChatMessage.model_validate(assistant_message, update={"owner_id": item_id})

    session.add(db_assistant_message)
    session.commit()
    session.refresh(db_assistant_message)

    return Message(message=response)


@router.get("/evaluate", response_model=EvaluationPublic)
async def evaluate_chatbot_radas(
    *, session: SessionDep, current_user: CurrentUser
) -> EvaluationPublic:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    quiz_evaluation = await quiz_eval.evaluate_quiz(session)
    summary_evaluation = await summary_eval.summary_eval()
    rag_evaluation = await RAG_eval.evaluate_RAG(session)
    return EvaluationPublic(quiz_evaluation=quiz_evaluation, summary_evaluation=summary_evaluation, rag_evaluation=rag_evaluation)


@router.get("/{item_id}", response_model=ChatMessagesPublic)
def get_chat_history(
    *, item_id: UUID, session: SessionDep, current_user: CurrentUser
) -> ChatMessagesPublic:
     
    statement = select(ChatMessage).where(ChatMessage.owner_id == item_id).order_by(ChatMessage.created_at)
    messages = session.exec(statement).all()

    if not current_user.is_superuser and ( messages and (messages[0].owner.owner_id != current_user.id)):
        raise HTTPException(status_code=400, detail="Not enough permissions")
     
    return ChatMessagesPublic(data=messages)
