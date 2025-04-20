from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from typing import List
from app.crud import *
from app.utility import *
from app.db import Base, engine, AsyncSessionLocal, get_session
import os

os.makedirs("uploaded_docs", exist_ok=True)

# Define lifespan with async context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables
    yield  # Start the app
    # Clean up or shutdown tasks can be placed here

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Pydantic models
class QuestionIn(BaseModel):
    question: str
    doc_ids: List[int]

class DocumentOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class DocumentSelection(BaseModel):
    doc_ids: List[int]

# API Endpoints

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        file_path = f"./uploaded_docs/{file.filename}"
        file_type = file.filename.split('.')[-1]

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        text = await extract_text_from_file(file_path, file_type)
        embedding = generate_embedding(text)

        # Use updated CRUD to save doc + embedding
        await save_document_and_embedding(file.filename, text, embedding)

        # Return immediately with doc_id
        return JSONResponse(content={"doc_id": file.filename})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/documents", response_model=List[DocumentOut])
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Document).offset(skip).limit(limit)
    result = await session.execute(stmt)
    docs = result.scalars().all()

    return docs

@app.post("/select_documents")
async def select_documents(payload: DocumentSelection, session: AsyncSession = Depends(get_session)):
    global user_selected_documents

    stmt = select(Document).where(Document.id.in_(payload.doc_ids))
    result = await session.execute(stmt)
    selected_docs = result.scalars().all()

    if not selected_docs:
        raise HTTPException(status_code=404, detail="No documents found with the given IDs.")

    user_selected_documents = selected_docs

    return {
        "message": "Documents selected successfully.",
        "selected_documents": [doc.name for doc in selected_docs]
    }


@app.post("/answer")
async def answer_question(payload: QuestionIn, session: AsyncSession = Depends(get_session)):
    try:
        # Check if doc_ids is empty
        if not payload.doc_ids:
            raise HTTPException(status_code=400, detail="No documents selected. Please select documents first.")

        query = payload.question
        query_embedding = generate_embedding(query)

        best_context = await search_best_context(session, query_embedding, payload.doc_ids)

        context_text = "\n".join([match[2] for match in best_context])
        answer = generate_answer(context_text, query)

        return {"answer": answer}

    except Exception as e:
        print(f"Error: {e}")  # This will help us log errors in the server logs
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")




