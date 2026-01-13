from fastapi import FastAPI
from .qdrant_db import get_qdrant_client
from .vector_store import ensure_collection
from .schemas import IngestRequest, AskRequest
from .ingest import ingest_text
from .ask import ask_rag
from .config import os
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, Form
from pypdf import PdfReader
import io

app = FastAPI(title="Mini RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/qdrant-check")
def qdrant_check():
    client = get_qdrant_client()
    collections = client.get_collections()
    return {"collections": [c.name for c in collections.collections]}

@app.post("/init")
def init_collection():
    client = get_qdrant_client()
    ensure_collection(client)
    return {"message": "Collection ready"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    result = ingest_text(title=req.title, text=req.text)
    return result

@app.post("/ask")
def ask(req: AskRequest):
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        return {"error": "GEMINI_API_KEY missing in .env"}

    result = ask_rag(question=req.question, gemini_api_key=gemini_key, top_k=5)
    return result

@app.post("/reset")
def reset_collection():
    client = get_qdrant_client()
    client.delete_collection(collection_name=os.getenv("QDRANT_COLLECTION", "mini_rag_docs"))
    ensure_collection(client)
    return {"message": "Collection reset done"}

@app.get("/stats")
def stats():
    client = get_qdrant_client()
    info = client.get_collection(os.getenv("QDRANT_COLLECTION", "mini_rag_docs"))
    return {
        "collection": os.getenv("QDRANT_COLLECTION", "mini_rag_docs"),
        "points_count": info.points_count
    }

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    title: str = Form("Uploaded Document")
):
    content = await file.read()
    extracted_text = ""

    if file.filename.lower().endswith(".txt"):
        extracted_text = content.decode("utf-8", errors="ignore")
    
    elif file.filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        pages_text = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")
        extracted_text = "\n".join(pages_text)
    
    else:
        return {"error": "Only .txt and .pdf files are supported."}

    result = ingest_text(title=title, text=extracted_text)
    return {
        "filename": file.filename,
        "title": title,
        "chars_extracted": len(extracted_text),
        "ingest_result": result
    }