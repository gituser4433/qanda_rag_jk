# Updated crud.py using SQLAlchemy (async)
from sqlalchemy.future import select
from app.models import Document, Embedding
from app.db import AsyncSessionLocal
from scipy.spatial.distance import cosine
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession


async def save_document_and_embedding(name: str, content: str, vector: list[float]):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            doc = Document(name=name, content=content)
            session.add(doc)
            await session.flush()  # Get ID after insert

            embedding = Embedding(document_id=doc.id, vector=vector)
            session.add(embedding)


async def search_best_context(session: AsyncSession, query_embedding: list[float], selected_documents: list[int],
                              top_n: int = 3):
    # Fetch the embeddings for the selected documents
    result = await session.execute(
        select(Embedding.vector, Document.name, Document.content)
        .join(Document)
        .filter(Document.id.in_(selected_documents))
    )

    embeddings = result.all()

    best_matches = []
    for emb in embeddings:
        stored_embedding = np.array(emb.vector)  # Stored embedding
        similarity = 1 - cosine(query_embedding, stored_embedding)  # Calculate cosine similarity
        best_matches.append((similarity, emb.name, emb.content))

    # Sort by similarity score (highest first)
    best_matches.sort(reverse=True, key=lambda x: x[0])

    # Return the top N best matches
    return best_matches[:top_n]