# Mini RAG Playground (Track B)
### **FastAPI + Qdrant + Gemini + Citations + File Upload**

A streamlined Retrieval-Augmented Generation (RAG) application that allows users to ingest text or upload documents, store chunk embeddings in a cloud-hosted vector database, and generate grounded answers with inline citations using a lightweight reranking step.

---

## Live Links
- **Frontend (Vercel):** https://minirag-three.vercel.app/
- **Backend (Render):** https://mini-rag-backendd.onrender.com

---

## Key Features

### RAG Pipeline
* **Multi-Source Ingestion:** Support for raw text pasting and file uploads (.txt / .pdf).
* **Vector Search:** Efficient retrieval using Qdrant Cloud.
* **Two-Step Retrieval:** Initial vector search followed by a similarity-based reranking step for higher precision.
* **Grounded Generation:** Answers powered by Gemini 1.5 Flash with inline citations (e.g., [1]) mapped to original source chunks.

### Production-Ready Design
* **Fully Hosted:** Decoupled frontend (Vercel) and backend (Render).
* **Security:** API keys and secrets managed strictly via server-side environment variables.
* **Testing Utilities:** Built-in endpoints for collection management and status monitoring.

---

## Technical Workflow

### 1. Ingestion and Indexing
* **Processing:** PDF/Text extraction followed by character-based chunking.
* **Embedding:** Each chunk is converted into a 768-dimensional vector using Gemini text-embedding-004.
* **Storage:** Vectors are upserted to Qdrant with a payload containing the title, text, chunk_index, and source.

### 2. Retrieval and Reranking
* **Retrieval:** The user's query is embedded, and the top 5 most similar candidates are fetched from Qdrant.
* **Reranking:** A secondary cosine similarity check is performed to select the top 3 most relevant chunks, filtering out low-confidence results based on a set threshold.

### 3. Generation
* The LLM receives the question and the context chunks (labeled [1], [2], etc.).
* The model generates a response strictly grounded in the provided context, including citations to maintain transparency and reduce hallucinations.

---

## Vector DB Configuration (Qdrant)

| Property | Value |
| :--- | :--- |
| **Provider** | Qdrant Cloud (Free Tier) |
| **Metric** | Cosine Similarity |
| **Embedding Model** | Gemini text-embedding-004 |
| **Dimensions** | 768 |
| **Chunk Size** | 1200 characters |
| **Overlap** | 150 characters |

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Returns API status. |
| **POST** | `/ingest` | Ingests raw text provided in JSON body. |
| **POST** | `/upload` | Ingests .pdf or .txt files via form-data. |
| **POST** | `/ask` | Queries the RAG pipeline for an answer. |
| **POST** | `/init` | Ensures the Qdrant collection is created. |
| **POST** | `/reset` | Deletes and recreates the collection (Testing only). |
| **GET** | `/stats` | Returns point counts and collection metadata. |

---

## Local Setup

### Backend
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with `QDRANT_URL`, `QDRANT_API_KEY`, and `GEMINI_API_KEY`.
4. Run the server: `uvicorn app.main:app --reload`

### Frontend
Simply open `frontend/index.html` in any modern web browser.

---

## Known Limitations
* **File Support:** Limited to .txt and .pdf only.
* **Chunking:** Currently uses character-based logic; token-based chunking is a planned improvement.
* **Reranker:** Uses a lightweight similarity check; integration with professional API rerankers (like Cohere or Jina) would further improve accuracy.

---

## Author
**Mann Ahalpara**
* **GitHub:** https://github.com/MannAhalpara
* **LinkedIn:** https://www.linkedin.com/in/mannahalpara/
* **Resume:** https://drive.google.com/file/d/1v2fil1I7i0_tqNGQSavIkv38i57x0OZ-/view?usp=drive_link
