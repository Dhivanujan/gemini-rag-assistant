# backend/services/rag_service.py

import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from pypdf import PdfReader

# Resolve root directory (3 levels up from backend/services/rag_service.py)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FOLDER = os.path.join(base_dir, "data")
VECTORSTORE_DIR = os.path.join(base_dir, "vectorstore")

os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text):
    embedding = embedding_model.encode(text)
    return np.array(embedding, dtype=np.float32)


def load_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def load_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_documents(data_folder=None):
    if data_folder is None:
        data_folder = DATA_FOLDER
    
    documents = []
    data_path = Path(data_folder)
    if not data_path.exists():
        return documents

    for file in data_path.iterdir():
        if file.suffix.lower() == ".pdf":
            documents.append(load_pdf(file))
        elif file.suffix.lower() == ".txt":
            documents.append(load_text_file(file))
            
    return documents


def chunk_text(text, chunk_size=500):
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def prepare_chunks(data_folder=None):
    if data_folder is None:
        data_folder = DATA_FOLDER
        
    docs = load_documents(data_folder)
    all_chunks = []
    
    data_path = Path(data_folder)
    text_files = list(data_path.glob("*.txt"))
    pdf_files = list(data_path.glob("*.pdf"))
    
    # If the file is only docs.txt and is small, split by \n\n to preserve paragraph structures
    if len(pdf_files) == 0 and len(text_files) == 1 and text_files[0].name == "docs.txt":
        content = load_text_file(text_files[0])
        chunks = content.split("\n\n")
        all_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    else:
        for doc in docs:
            chunks = chunk_text(doc)
            all_chunks.extend(chunks)
            
    return all_chunks


def build_vector_store(chunks):
    if not chunks:
        dimension = 384
        return faiss.IndexFlatL2(dimension)
        
    embeddings = np.array([get_embedding(chunk) for chunk in chunks])
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def save_index(index, filename="knowledge.index"):
    path = os.path.join(VECTORSTORE_DIR, filename)
    faiss.write_index(index, path)


def save_chunks(chunks, filename="knowledge_chunks.pkl"):
    path = os.path.join(VECTORSTORE_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(chunks, f)


def load_index(filename="knowledge.index"):
    path = os.path.join(VECTORSTORE_DIR, filename)
    if os.path.exists(path):
        return faiss.read_index(path)
    return None


def load_chunks(filename="knowledge_chunks.pkl"):
    path = os.path.join(VECTORSTORE_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return []


def search(query, index, chunks, k=3):
    if not chunks or index is None or index.ntotal == 0:
        return []

    k = min(k, len(chunks))
    query_embedding = get_embedding(query)
    query_embedding = np.array([query_embedding])

    distances, indices = index.search(query_embedding, k)

    results = []
    for idx in indices[0]:
        if idx != -1 and idx < len(chunks):
            results.append(chunks[idx])

    return results


def get_context(query, index, chunks):
    docs = search(query, index, chunks)
    return "\n\n".join(docs)


def get_knowledge_base():
    index_path = os.path.join(VECTORSTORE_DIR, "knowledge.index")
    chunks_path = os.path.join(VECTORSTORE_DIR, "knowledge_chunks.pkl")
    
    if os.path.exists(index_path) and os.path.exists(chunks_path):
        try:
            idx = faiss.read_index(index_path)
            with open(chunks_path, "rb") as f:
                chks = pickle.load(f)
            return idx, chks
        except Exception:
            pass
            
    # Rebuild
    chks = prepare_chunks()
    idx = build_vector_store(chks)
    
    # Save cache
    save_index(idx)
    save_chunks(chks)
        
    return idx, chks


# Cache instance
_knowledge_index = None
_knowledge_chunks = None

def get_knowledge_base_index():
    global _knowledge_index, _knowledge_chunks
    if _knowledge_index is None or _knowledge_chunks is None:
        _knowledge_index, _knowledge_chunks = get_knowledge_base()
    return _knowledge_index, _knowledge_chunks


if __name__ == "__main__":
    print("Rebuilding knowledge base...")
    chunks = prepare_chunks()
    index = build_vector_store(chunks)
    save_index(index)
    save_chunks(chunks)
    print(f"Knowledge base built with {len(chunks)} chunks.")
