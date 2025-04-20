from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from app.db import Base
from sqlalchemy import ForeignKey

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    content = Column(String)

class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    vector = Column(Vector(1536))  # 1536 is the embedding size of ada-002
