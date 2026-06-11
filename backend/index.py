# build_index.py

from backend.ingest import prepare_chunks
from backend.rag import build_vector_store
from backend.rag import save_index
from backend.rag import save_chunks

chunks = prepare_chunks()

index = build_vector_store(chunks)

save_index(index)
save_chunks(chunks)

print("Knowledge base built.")