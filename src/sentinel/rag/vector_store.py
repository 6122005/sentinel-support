"""Production-grade Vector Database (ChromaDB) for Sentinel Knowledge Base.

Provides semantic search (RAG) over support articles instead of naive keyword matching.
"""

import json
from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings

_DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "kb_articles.json"
_DB_PATH = Path(__file__).resolve().parents[3] / ".chroma_db"

_INSTANCE: "KnowledgeBaseVectorStore | None" = None


class KnowledgeBaseVectorStore:
    """Manages indexing and semantic retrieval of internal knowledge base articles."""

    def __init__(self, persist_dir: Path | str | None = None) -> None:
        if persist_dir:
            self.client = chromadb.PersistentClient(path=str(persist_dir))
        else:
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))

        self.collection = self.client.get_or_create_collection(
            name="sentinel_support_kb",
            metadata={"description": "Sentinel Support Knowledge Base Articles"},
        )
        self._ensure_indexed()

    def _ensure_indexed(self) -> None:
        """Seed the vector database if the collection is empty."""
        if self.collection.count() > 0:
            return

        if not _DATA_PATH.exists():
            return

        articles = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for item in articles:
            ids.append(item["id"])
            # Embed combined title and body for rich semantic context
            doc_text = f"Title: {item['title']}\nContent: {item['body']}"
            documents.append(doc_text)
            metadatas.append({
                "id": item["id"],
                "title": item["title"],
                "body": item["body"],
            })

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        top_k: int = 2,
        max_distance: float = 1.15,
    ) -> list[dict[str, Any]]:
        """Semantic vector search across knowledge base articles.

        Args:
            query: The user's query or issue description.
            top_k: Number of most relevant articles to return.
            max_distance: Distance cutoff (lower is more similar). Results with
                          distance > max_distance are discarded as irrelevant.

        Returns:
            List of matching article dictionaries with 'id', 'title', 'body',
            and 'distance'.
        """
        if not query.strip() or self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
            include=["metadatas", "documents", "distances"],
        )

        matches: list[dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return matches

        ids = results["ids"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for i, article_id in enumerate(ids):
            dist = float(distances[i]) if i < len(distances) else 1.0
            meta = metadatas[i] if i < len(metadatas) else {}

            # Strict relevance filter: reject if semantic distance is too high
            if dist <= max_distance and meta:
                matches.append({
                    "id": meta.get("id", article_id),
                    "title": meta.get("title", ""),
                    "body": meta.get("body", ""),
                    "distance": round(dist, 4),
                    "similarity_score": round(max(0.0, 1.0 - (dist / 2.0)), 4),
                })

        return matches


def get_kb_vector_store() -> KnowledgeBaseVectorStore:
    """Singleton getter for the knowledge base vector store."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = KnowledgeBaseVectorStore(persist_dir=_DB_PATH)
    return _INSTANCE
