# rag.py
import chromadb

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "beneficios_sp"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)

def query_benefits(text: str):
    """Retorna os benefícios mais relevantes para o que o usuário falou."""

    results = collection.query(
        query_texts=[text],
        n_results=3
    )

    if not results["documents"] or len(results["documents"][0]) == 0:
        return None

    context = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context.append(
            f"- **{meta['programa']}** → {doc}"
        )

    return "\n".join(context)
