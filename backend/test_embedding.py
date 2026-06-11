import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag import get_embedding

embedding = get_embedding("Hello world")
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding type: {embedding.dtype}")