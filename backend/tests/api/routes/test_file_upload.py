import uuid
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Document
from tests.utils.document import create_document_with_chunk
from tests.utils.item import create_random_item


def test_read_documents_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/upload/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_read_documents_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    doc = Document(
        title="Doc",
        content="c",
        summary="s",
        owner_id=item.id,
    )
    db.add(doc)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/upload/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["title"] == "Doc"


def test_read_documents_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    doc = Document(
        title="Doc",
        content="c",
        summary="s",
        owner_id=item.id,
    )
    db.add(doc)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/upload/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough permissions"


@patch("app.api.routes.file_upload.summarization_model.generate_item_summary", new_callable=AsyncMock)
@patch("app.api.routes.file_upload.summarization_model.summarize_file", new_callable=AsyncMock)
@patch("app.api.routes.file_upload.preprocess.preprocess_text_for_chat", new_callable=AsyncMock)
@patch("app.api.routes.file_upload.preprocess.preprocess_input", new_callable=AsyncMock)
def test_upload_file_success(
    mock_preprocess_input: AsyncMock,
    mock_preprocess_chat: AsyncMock,
    mock_summarize: AsyncMock,
    mock_item_summary: AsyncMock,
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    mock_preprocess_input.return_value = {
        "clean_text": "hello world",
        "chunks": ["hello world"],
    }
    mock_summarize.return_value = "file summary"
    mock_item_summary.return_value = "combined item summary"

    item = create_random_item(db)
    file_content = b"hello world"
    response = client.post(
        f"{settings.API_V1_STR}/upload/{item.id}",
        headers=superuser_token_headers,
        files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "combined item summary"
    assert body["document"]["title"] == "test.txt"
    mock_preprocess_chat.assert_called_once()


def test_upload_file_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/upload/{uuid.uuid4()}",
        headers=superuser_token_headers,
        files={"file": ("a.txt", BytesIO(b"x"), "text/plain")},
    )
    assert response.status_code == 404


def test_upload_file_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.post(
        f"{settings.API_V1_STR}/upload/{item.id}",
        headers=normal_user_token_headers,
        files={"file": ("a.txt", BytesIO(b"x"), "text/plain")},
    )
    assert response.status_code == 400


@patch(
    "app.api.routes.file_upload.summarization_model.generate_item_summary",
    new_callable=MagicMock,
)
def test_delete_document_success(
    mock_item_summary: MagicMock,
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    mock_item_summary.return_value = "updated summary"
    item = create_random_item(db)
    doc, _ = create_document_with_chunk(db, item)

    response = client.delete(
        f"{settings.API_V1_STR}/upload/{doc.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "updated summary"


def test_delete_document_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.file_upload.summarization_model.generate_item_summary",
        MagicMock(return_value="x"),
    ):
        response = client.delete(
            f"{settings.API_V1_STR}/upload/{uuid.uuid4()}",
            headers=superuser_token_headers,
        )
    assert response.status_code == 404


def test_delete_document_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    doc, _ = create_document_with_chunk(db, item)
    with patch(
        "app.api.routes.file_upload.summarization_model.generate_item_summary",
        MagicMock(return_value="x"),
    ):
        response = client.delete(
            f"{settings.API_V1_STR}/upload/{doc.id}",
            headers=normal_user_token_headers,
        )
    assert response.status_code == 400
