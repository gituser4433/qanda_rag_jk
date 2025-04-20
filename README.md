# Document Management and RAG-based Q&A Application

## Project Overview
This project is a backend application built to handle document ingestion, embedding generation, and Q&A functionality based on a **Retrieval-Augmented Generation (RAG)** system. The backend exposes APIs for:

1. **Document Ingestion**: Accepts document files, generates embeddings, and stores them for future retrieval.
2. **Document Selection**: Allows users to select documents for the Q&A process.
3. **Q&A via ChatGPT**: Accepts user queries, retrieves relevant documents, and generates answers using the RAG system.

## Architecture

### **Backend Components**:
1. **FastAPI**:
   - The web framework that serves the APIs for document ingestion and Q&A.
   - It also provides asynchronous processing to handle large volumes of requests.

2. **Document Ingestion**:
   - Endpoint: `POST /ingest`
   - Accepts uploaded documents, processes them, and stores the embeddings in the database.
   
3. **Q&A**:
   - Endpoint: `POST /answer`
   - Accepts user queries and selected document IDs, retrieves relevant document embeddings, and generates an answer using the **OpenAI API**.

4. **Database**:
   - **PostgreSQL** stores document embeddings for retrieval.
   - Embeddings are generated using the **OpenAI API**'s `text-embedding-ada-002` model.

5. **OpenAI API**:
   - For document embedding generation and query-answer generation (RAG-based).

6. **Asynchronous Processing**:
   - Utilizes **asyncpg** with SQLAlchemy for efficient database handling.

### **Database Schema**:
- **Documents**: Stores information about the documents.
  - `id` (Primary Key)
  - `name` (Document name)
  - `embedding` (Document embedding, vector representation)

## Run Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Document-QA-System.git
cd Document-QA-System
