from openai import OpenAI
import os
import PyPDF2
import docx
import textwrap
from app.crud import save_document_and_embedding

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

async def extract_text_from_file(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        return await extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return await extract_text_from_docx(file_path)
    elif file_type == "txt":
        return await extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file type")

async def extract_text_from_pdf(file_path: str) -> str:
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

async def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

async def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


async def process_file_embedding(filename: str, path: str, file_type: str):
    try:
        text = await extract_text_from_file(path, file_type)
        embedding = generate_embedding(text)
        await save_document_and_embedding(filename, text, embedding)
    except Exception as e:
        print(f"Background task failed: {e}")

# Function to split the text into smaller chunks
def chunk_text(text: str, max_tokens: int = 8192):
    # Split the text into chunks of `max_tokens`
    words = text.split()
    chunk_size = max_tokens // 4  # Estimate 1 token = 4 chars, so divide accordingly

    chunks = [
        ' '.join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    return chunks


def generate_embedding(text: str) -> list[float]:
    try:
        # Break the text into ~1500-character chunks to stay well under token limits
        chunks = textwrap.wrap(text, width=1500)
        all_embeddings = []

        for chunk in chunks:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )
            embedding = response.data[0].embedding
            all_embeddings.append(embedding)

        # Average the embeddings
        avg_embedding = [sum(x) / len(x) for x in zip(*all_embeddings)]
        return avg_embedding

    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")


def truncate_text(text, max_chars=6000):
    return text[:max_chars] if len(text) > max_chars else text



def generate_answer(context: str, question: str):
    context = truncate_text(context)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": context},
        {"role": "user", "content": question},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            timeout=10,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {e}"
