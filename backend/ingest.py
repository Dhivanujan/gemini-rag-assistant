# backend/ingest.py

from pathlib import Path
from pypdf import PdfReader
import pickle
import faiss


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


def load_documents(data_folder="data"):

    documents = []

    for file in Path(data_folder).iterdir():

        if file.suffix.lower() == ".pdf":
            documents.append(load_pdf(file))

        elif file.suffix.lower() == ".txt":
            documents.append(load_text_file(file))

    return documents

def chunk_text(text, chunk_size=500):

    chunks = []

    words = text.split()

    for i in range(
        0,
        len(words),
        chunk_size
    ):
        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks

def prepare_chunks():

    docs = load_documents()

    all_chunks = []

    for doc in docs:

        chunks = chunk_text(doc)

        all_chunks.extend(chunks)

    return all_chunks

def save_index(index):

    faiss.write_index(
        index,
        "vectorstore/knowledge.index"
    )

def save_chunks(chunks):

    with open(
        "vectorstore/knowledge_chunks.pkl",
        "wb"
    ) as f:

        pickle.dump(chunks, f)

def load_index():

    return faiss.read_index(
        "vectorstore/knowledge.index"
    )

def load_chunks():

    with open(
        "vectorstore/knowledge_chunks.pkl",
        "rb"
    ) as f:

        return pickle.load(f)