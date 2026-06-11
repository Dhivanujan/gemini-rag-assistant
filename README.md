# AI RAG Chatbot

An intelligent, lightweight Retrieval-Augmented Generation (RAG) chatbot backend built with **FastAPI**, **FAISS**, and the **Google Gemini API**.

---

## 🚀 Key Features

* **Efficient Vector Search:** Chunks documents and creates semantic embeddings using Hugging Face's `sentence-transformers` (`all-MiniLM-L6-v2`) and indexes them using a **FAISS** vector database.
* **Gemini LLM Integration:** Uses the latest `google-genai` SDK to query Gemini (`gemini-2.5-flash` with a fallback to `gemini-2.5-flash-lite`).
* **Resilient API:** Includes automatic retry mechanisms with exponential backoff on transient Google API rate-limit (`429`) or server-overload (`503`) errors.
* **Frontend-Ready (CORS enabled):** Pre-configured with CORS middleware to allow cross-origin requests from frontend apps (e.g. React/Vite running on localhost).
* **Location-Independent execution:** Configured with absolute paths so the server can be started from any directory without losing access to `.env` or data files.

---

## 📂 Project Structure

```text
AI-RAG-Chatbot/
├── backend/
│   ├── config.py           # Configuration and environment variables loader
│   ├── llm.py              # LLM response generation with retries & fallbacks
│   ├── main.py             # FastAPI server entry point and CORS configuration
│   ├── memory.py           # Placeholder for conversation memory extensions
│   ├── rag.py              # Document loading, embedding, and FAISS indexing
│   └── test_embedding.py   # Quick verification script for embeddings
├── data/
│   └── docs.txt            # Document corpus (knowledge base) used for RAG context
├── vectorstore/            # Directory for local database artifacts
├── .env                    # Local environment secrets (ignored by git)
├── .gitignore              # Configured patterns to prevent tracking secrets/venv
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Configure Environment Variables
Create a file named `.env` in the root of the project (already ignored in `.gitignore`) and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Create & Activate Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚡ Running the Server

Start the development server using Uvicorn:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The server will automatically load documents from `data/docs.txt`, build the FAISS index in-memory, and start listening on `http://127.0.0.1:8000`.

---

## 🔌 API Documentation

### POST `/chat`
Generates a response to a question using the retrieved document context.

#### **Request Body**
```json
{
  "message": "What is the LMS System?"
}
```

#### **Response Body**
```json
{
  "question": "What is the LMS System?",
  "context": "LMS System:\nThe LMS includes course management, user roles, and certificates.\nIt is built using FastAPI and React.",
  "answer": "The LMS System includes course management, user roles, and certificates. It is built using FastAPI and React."
}
```
