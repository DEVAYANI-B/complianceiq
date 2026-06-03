import chromadb
from chromadb.config import Settings
import uuid
import os


DATA_DIR = os.path.join(os.getcwd(), "data", "vectorstore")
os.makedirs(DATA_DIR, exist_ok=True)

client = chromadb.PersistentClient(path="data/vectorstore")
collection = client.get_or_create_collection(name="complianceiq_docs")

def store_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """Store text chunks and their embeddings in ChromaDB."""
    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks]
    )

def retrieve_relevant_chunks(query_embedding: list[float], n_results: int = 5, doc_type: str | None = None) -> list[dict]:
    """Retrieve top-n relevant chunks for a query, optionally filtered by doc_type."""
    where = {"doc_type": doc_type} if doc_type else None
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": results["distances"][0][i]
        })
    return chunks
def get_all_chunks_for_doc(doc_name: str) -> list[dict]:
    """Retrieve all chunks belonging to a specific document."""
    try:
        results = collection.get(
            where={"doc_name": doc_name},
            include=["documents", "metadatas"]
        )
        chunks = []
        for i in range(len(results["documents"])):
            chunks.append({
                "text": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        return chunks
    except Exception:
        return []