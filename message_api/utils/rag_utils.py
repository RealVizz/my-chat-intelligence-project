import chromadb
from sentence_transformers import SentenceTransformer

from message_api import config

_client = None
_collection = None
_model = None

COLLECTION_NAME = "messages"
MODEL_NAME = "all-MiniLM-L6-v2"


def initialize_rag():
    """Initializes the RAG model and vector store client."""
    global _client, _collection, _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.DATA_DIR / "chroma_db"))

    if _collection is None:
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)


def add_document_to_store(doc_id: str, document: str):
    """Generates an embedding for a document and adds it to the vector store."""
    if _collection is None or _model is None:
        return

    embedding = _model.encode(document, convert_to_tensor=False)
    _collection.add(
        documents=[document],
        embeddings=[embedding.tolist()],
        ids=[doc_id]
    )


def find_relevant_documents(query: str, filter_ids: list[str] = None, top_k: int = 5):
    """Finds relevant document IDs for a query, with an optional filter."""
    if _collection is None or _model is None:
        return []

    query_embedding = _model.encode(query, convert_to_tensor=False)

    if filter_ids:
        # ChromaDB's 'where' clause for filtering is more robust for this.
        # Creating a filter to match any of the provided IDs.
        where_filter = {"$or": [{"id": doc_id} for doc_id in filter_ids]}
        results = _collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter
        )
    else:
        results = _collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

    return results['ids'][0] if results and 'ids' in results else []
