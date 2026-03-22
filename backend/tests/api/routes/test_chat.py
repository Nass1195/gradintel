import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import (
    ChatMessage,
    MCQEvaluation,
    RAGEvaluation,
    RAGEvaluationOutput,
    bertEvaluation,
)
from tests.utils.item import create_random_item


def test_get_chat_history_empty(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/chat/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_chat_history_unknown_item_returns_empty_for_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """History does not validate item existence; missing items yield no messages."""
    missing_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/chat/{missing_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_chat_history_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    db.add(ChatMessage(message="hi", role="user", owner_id=item.id))
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/chat/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough permissions"


@patch("app.api.routes.chat.chatbot.generate_chat_response", new_callable=AsyncMock)
def test_chat_with_document(
    mock_response: AsyncMock,
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    mock_response.return_value = ("Assistant reply", None)
    item = create_random_item(db)
    response = client.post(
        f"{settings.API_V1_STR}/chat/{item.id}",
        headers=superuser_token_headers,
        json={"message": "Hello"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Assistant reply"
    mock_response.assert_called_once()


def test_chat_with_document_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/chat/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json={"message": "Hello"},
    )
    assert response.status_code == 404


def test_chat_with_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.post(
        f"{settings.API_V1_STR}/chat/{item.id}",
        headers=normal_user_token_headers,
        json={"message": "Hello"},
    )
    assert response.status_code == 400


@patch("app.api.routes.chat.RAG_eval.evaluate_RAG", new_callable=AsyncMock)
@patch("app.api.routes.chat.summary_eval.summary_eval", new_callable=AsyncMock)
@patch("app.api.routes.chat.quiz_eval.evaluate_quiz", new_callable=AsyncMock)
def test_evaluate_chatbot_superuser(
    mock_quiz: AsyncMock,
    mock_summary: AsyncMock,
    mock_rag: AsyncMock,
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    mock_quiz.return_value = [
        MCQEvaluation(
            accuracy_score=5,
            clarity_score=5,
            distractor_score=5,
            total_score=15,
            reasoning="ok",
        )
    ]
    mock_summary.return_value = [
        bertEvaluation(precision=0.5, recall=0.5, f1_score=0.5)
    ]
    mock_rag.return_value = RAGEvaluationOutput(
        similarity_scores=[0.5],
        evaluations=[
            RAGEvaluation(
                relevance_score=0.5,
                accuracy_score=0.5,
                completeness_score=0.5,
                overall_score=0.5,
                explanation="ok",
            )
        ],
    )
    response = client.get(
        f"{settings.API_V1_STR}/chat/evaluate",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["quiz_evaluation"]) == 1
    assert len(body["summary_evaluation"]) == 1
    assert body["rag_evaluation"]["similarity_scores"] == [0.5]


def test_evaluate_chatbot_forbidden_for_non_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/chat/evaluate",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough permissions"
