import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import QuizQuestion
from tests.utils.document import create_document_with_chunk
from tests.utils.item import create_random_item


def test_get_quiz_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/quiz/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "quiz not found"


def test_get_quiz_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    _, chunk = create_document_with_chunk(db, item)
    qq = QuizQuestion(
        question="What?",
        options=["a", "b"],
        correct_answer="a",
        explanation="because",
        item_id=item.id,
        chunk_id=chunk.id,
    )
    db.add(qq)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/quiz/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough permissions"


def test_get_quiz_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    _, chunk = create_document_with_chunk(db, item)
    qq = QuizQuestion(
        question="What?",
        options=["a", "b"],
        correct_answer="a",
        explanation="because",
        item_id=item.id,
        chunk_id=chunk.id,
    )
    db.add(qq)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/quiz/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question"] == "What?"


@patch("app.api.routes.quiz.quiz_model.generate_quiz", new_callable=AsyncMock)
def test_generate_quiz_endpoint(
    mock_generate: AsyncMock,
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    item = create_random_item(db)
    _, chunk = create_document_with_chunk(db, item)
    existing = QuizQuestion(
        question="Old?",
        options=["x"],
        correct_answer="x",
        explanation="old",
        item_id=item.id,
        chunk_id=chunk.id,
    )
    mock_generate.return_value = ([existing], ["chunk text"])

    response = client.get(
        f"{settings.API_V1_STR}/quiz/generate/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["questions"][0]["question"] == "Old?"


def test_generate_quiz_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/quiz/generate/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_generate_quiz_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    with patch(
        "app.api.routes.quiz.quiz_model.generate_quiz",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = ([], [])
        response = client.get(
            f"{settings.API_V1_STR}/quiz/generate/{item.id}",
            headers=normal_user_token_headers,
        )
    assert response.status_code == 400


def test_complete_quiz_updates_chunks(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    _, chunk = create_document_with_chunk(db, item)
    qq = QuizQuestion(
        question="Q?",
        options=["a", "b"],
        correct_answer="a",
        explanation="e",
        item_id=item.id,
        chunk_id=chunk.id,
    )
    db.add(qq)
    db.commit()
    db.refresh(qq)
    db.refresh(chunk)

    payload = {
        "questions": [
            {
                "id": str(qq.id),
                "question": qq.question,
                "options": qq.options,
                "correct_answer": qq.correct_answer,
                "explanation": qq.explanation,
                "chunk_id": str(chunk.id),
                "is_correct": True,
            }
        ]
    }
    response = client.post(
        f"{settings.API_V1_STR}/quiz/complete",
        headers=superuser_token_headers,
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "answer received"

    db.refresh(chunk)
    assert chunk.num_answered_questions == 1
    assert chunk.correct_answers == 1


def test_complete_quiz_chunks_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    payload = {
        "questions": [
            {
                "id": str(uuid.uuid4()),
                "question": "Q?",
                "options": ["a"],
                "correct_answer": "a",
                "explanation": "e",
                "chunk_id": str(uuid.uuid4()),
                "is_correct": True,
            }
        ]
    }
    response = client.post(
        f"{settings.API_V1_STR}/quiz/complete",
        headers=superuser_token_headers,
        json=payload,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "chunks not found"


def test_complete_quiz_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    _, chunk = create_document_with_chunk(db, item)
    qq = QuizQuestion(
        question="Q?",
        options=["a", "b"],
        correct_answer="a",
        explanation="e",
        item_id=item.id,
        chunk_id=chunk.id,
    )
    db.add(qq)
    db.commit()
    db.refresh(qq)

    payload = {
        "questions": [
            {
                "id": str(qq.id),
                "question": qq.question,
                "options": qq.options,
                "correct_answer": qq.correct_answer,
                "explanation": qq.explanation,
                "chunk_id": str(chunk.id),
                "is_correct": True,
            }
        ]
    }
    response = client.post(
        f"{settings.API_V1_STR}/quiz/complete",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert response.status_code == 400
