"""Tests for ChromaDB Vector RAG Store."""

from sentinel.rag.vector_store import KnowledgeBaseVectorStore


def test_vector_store_indexing_and_search():
    store = KnowledgeBaseVectorStore(persist_dir=None)
    assert store.collection.count() >= 4

    # Semantic search with natural language phrasing
    results = store.search("The application keeps crashing every time I sign in", top_k=1)
    assert len(results) > 0
    top = results[0]
    assert top["id"] == "kb_001"
    assert "login" in top["title"].lower() or "crash" in top["title"].lower()
    assert "similarity_score" in top


def test_vector_store_irrelevant_query():
    store = KnowledgeBaseVectorStore(persist_dir=None)
    # Complete gibberish query should be filtered out by max_distance
    results = store.search("astronomy mars rover satellite spaceship galaxy", top_k=1, max_distance=0.5)
    assert len(results) == 0
