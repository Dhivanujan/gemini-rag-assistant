# backend/rag.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model once
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def load_documents(file_path=None):
    if file_path is None:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "docs.txt")
        
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # simple chunking (we improve later)
    chunks = text.split("\n\n")

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def get_embedding(text):
    embedding = embedding_model.encode(text)

    return np.array(
        embedding,
        dtype=np.float32
    )


def build_vector_store(chunks):

    embeddings = np.array(
        [get_embedding(chunk) for chunk in chunks]
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def search(query, index, chunks, k=3):
    if not chunks:
        return []

    k = min(k, len(chunks))
    query_embedding = get_embedding(query)

    query_embedding = np.array(
        [query_embedding]
    )

    distances, indices = index.search(
        query_embedding,
        k
    )

    results = []
    for idx in indices[0]:
        if idx != -1:
            results.append(chunks[idx])

    return results


def get_context(query, index, chunks):

    docs = search(
        query,
        index,
        chunks
    )

    return "\n\n".join(docs)