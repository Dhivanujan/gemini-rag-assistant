# tests/test_refactoring.py

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Append project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestRefactoring(unittest.TestCase):

    def test_config(self):
        from backend.core.config import GEMINI_API_KEY, MONGODB_URI, MONGODB_DB_NAME
        self.assertIsNotNone(GEMINI_API_KEY)
        self.assertIsNotNone(MONGODB_URI)
        self.assertIsNotNone(MONGODB_DB_NAME)

    def test_embedding_generation(self):
        from backend.services.rag_service import get_embedding
        embedding = get_embedding("Hello world")
        self.assertEqual(embedding.shape, (384,))
        self.assertEqual(str(embedding.dtype), "float32")

    def test_memory_paths_resolution(self):
        from backend.services.memory_service import get_memory_paths
        index_path, chunks_path = get_memory_paths("test_session/../evil")
        # Ensure path traversal is mitigated
        self.assertIn("memory_test_sessionevil.index", index_path)

    @patch("backend.services.llm_service.client")
    def test_llm_response_generation(self, mock_client):
        from backend.services.llm_service import generate_response
        
        # Mock response from Gemini
        mock_response = MagicMock()
        mock_response.text = "Hello! I am Gemini."
        mock_client.models.generate_content.return_value = mock_response
        
        resp = generate_response("Hi", "context", "User: Hi")
        self.assertEqual(resp, "Hello! I am Gemini.")
        mock_client.models.generate_content.assert_called_once()

    @patch("backend.services.llm_service.client")
    def test_llm_response_stream_generation(self, mock_client):
        from backend.services.llm_service import generate_response_stream
        
        # Mock stream chunks from Gemini
        chunk1 = MagicMock()
        chunk1.text = "Hello "
        chunk2 = MagicMock()
        chunk2.text = "streaming!"
        
        mock_client.models.generate_content_stream.return_value = [chunk1, chunk2]
        
        chunks = list(generate_response_stream("Hi", "context", "User: Hi"))
        self.assertEqual(chunks, ["Hello ", "streaming!"])
        mock_client.models.generate_content_stream.assert_called_once()


if __name__ == "__main__":
    unittest.main()
