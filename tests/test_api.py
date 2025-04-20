import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
import asyncio

client = TestClient(app)

# Set up the async event loop for pytest
@pytest_asyncio.fixture(scope="function")
async def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Test POST /ingest
def test_ingest_document():
    file_content = b"Example document content."
    response = client.post(
        "/ingest",
        files={"file": ("test_document.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    assert "doc_id" in response.json()

# Test GET /documents
def test_get_documents():
    response = client.get("/documents?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test POST /answer
def test_answer_question():
    # Ingest a document first
    file_content = b"Document content for answering."
    response = client.post(
        "/ingest",
        files={"file": ("doc1.txt", file_content, "text/plain")}
    )

    # Ensure the document ingestion was successful
    assert response.status_code == 200
    doc_id = response.json().get("doc_id")
    assert doc_id is not None

    # Now, ask a question related to the ingested document
    question_data = {"question": "What is this document about?", "doc_ids": [int(doc_id)]}
    response = client.post("/answer", json=question_data)

    assert response.status_code == 200
    assert "answer" in response.json()

def test_answer_no_documents():
    question_data = {"question": "What is this document about?", "doc_ids": []}
    response = client.post("/answer", json=question_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "No documents selected. Please select documents first."


