import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from backend.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Hello world"
)

print(len(response.embeddings[0].values))