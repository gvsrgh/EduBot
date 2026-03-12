"""
Vector Store Module — Qdrant Cloud Integration

Handles document embedding, storage, and semantic search using:
- FastEmbed (all-MiniLM-L6-v2) for lightweight ONNX-based embeddings
- Qdrant Cloud for vector storage and similarity search

Documents are chunked (500-1000 tokens, 10% overlap), embedded,
and stored with category metadata for domain-aware retrieval.
"""

import uuid
import numpy as np
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from fastembed import TextEmbedding


# ── Configuration ──────────────────────────────────────────────
from app.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

COLLECTION_NAME = QDRANT_COLLECTION
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimension of all-MiniLM-L6-v2
CHUNK_SIZE = 800     # ~800 characters per chunk
CHUNK_OVERLAP = 80   # ~10% overlap
SIMILARITY_THRESHOLD = 0.20
TOP_K = 5


# ── Singleton Instances ───────────────────────────────────────
_embedding_model: Optional[TextEmbedding] = None
_qdrant_client: Optional[QdrantClient] = None


def get_embedding_model() -> TextEmbedding:
    """Lazy-load the FastEmbed model (ONNX-based, lightweight)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)
        print("Embedding model loaded")
    return _embedding_model


def get_qdrant_client() -> QdrantClient:
    """Lazy-load the Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        print(f"Connecting to Qdrant at {QDRANT_URL}")
        _qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        print("Qdrant client connected")
    return _qdrant_client


# ── Collection Setup ──────────────────────────────────────────
def ensure_collection():
    """Create the Qdrant collection if it doesn't exist."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        print(f"Creating collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"Collection '{COLLECTION_NAME}' created")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")

    # Ensure payload index on 'category' for filtered searches
    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception:
        pass  # Index already exists


# ── Text Chunking ─────────────────────────────────────────────
def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into chunks of approximately chunk_size characters
    with overlap between consecutive chunks.

    Uses paragraph boundaries when possible to preserve context.
    """
    if not text or not text.strip():
        return []

    # Split by double-newlines (paragraphs) first
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk_size, save current and start new
        if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap from the end of the current chunk
            if overlap > 0:
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            current_chunk = (
                current_chunk + "\n\n" + para if current_chunk else para
            )

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ── Filename Context ───────────────────────────────────────────
def _filename_to_context(filename: str) -> str:
    """Convert a filename into a human-readable context prefix.

    Example:
        'scraped_pvpsiddhartha_feestructure.txt'
        → 'Document: scraped pvpsiddhartha feestructure'

    This prefix is prepended to chunk text *before* embedding so that
    filename semantics (e.g. 'fee', 'admission', 'hostel') are captured
    in the vector representation.
    """
    import re as _re
    stem = filename.rsplit(".", 1)[0]  # drop extension
    # Replace underscores, hyphens, and camelCase boundaries with spaces
    readable = _re.sub(r"[_\-]+", " ", stem)
    readable = _re.sub(r"(?<=[a-z])(?=[A-Z])", " ", readable)
    return f"Document: {readable.strip()}"


# ── Embedding ─────────────────────────────────────────────────
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using FastEmbed."""
    model = get_embedding_model()
    embeddings = list(model.embed(texts))
    return [emb.tolist() if isinstance(emb, np.ndarray) else list(emb) for emb in embeddings]


# ── Indexing (Upload) ─────────────────────────────────────────
def index_document(
    text: str,
    filename: str,
    category: str,
) -> tuple[int, List[str]]:
    """
    Process a document: chunk → embed → store in Qdrant.

    Returns a tuple of (chunk_count, list_of_vector_point_ids).
    """
    ensure_collection()
    client = get_qdrant_client()

    # Remove any existing chunks for this file first (re-index support)
    try:
        delete_document(filename, category)
    except Exception:
        pass

    # Chunk the text
    chunks = chunk_text(text)
    if not chunks:
        return 0, []

    # Prepend filename context so filename semantics are captured in embeddings
    file_context = _filename_to_context(filename)
    enriched_chunks = [f"{file_context}\n\n{chunk}" for chunk in chunks]

    # Generate embeddings from enriched text (includes filename context)
    embeddings = embed_texts(enriched_chunks)

    # Build Qdrant points (store original chunk text in payload, not enriched)
    points = []
    point_ids: List[str] = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())
        point_ids.append(point_id)
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "filename": filename,
                    "category": category,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            )
        )

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)

    print(f"Indexed {len(chunks)} chunks from '{filename}' [{category}]")
    return len(chunks), point_ids


# ── Search ────────────────────────────────────────────────────
def _extract_filename_keywords(query: str) -> List[str]:
    """Extract meaningful keywords from a query for filename matching."""
    import re as _re
    # Normalise and split into words (3+ chars to avoid noise)
    words = _re.findall(r"[a-zA-Z]{3,}", query.lower())
    # Remove very common stop-words that would cause false-positive filename hits
    stop = {
        "the", "and", "for", "are", "but", "not", "you", "all",
        "can", "had", "her", "was", "one", "our", "out", "has",
        "what", "when", "who", "how", "where", "which", "this",
        "that", "with", "from", "about", "tell", "give", "please",
        "details", "detail", "info", "information", "know", "want",
    }
    return [w for w in words if w not in stop]


def search_documents(
    query: str,
    category: Optional[str] = None,
    top_k: int = TOP_K,
    threshold: float = SIMILARITY_THRESHOLD,
) -> List[dict]:
    """
    Semantic search across indexed documents with filename-aware boosting.

    Performs a two-pass search:
      1. Standard vector similarity search.
      2. Filename-keyword match — scrolls through stored filenames and
         retrieves additional chunks from files whose names contain query
         keywords.  These results are merged (deduplicated) with the
         vector hits so that relevant files are never missed just because
         the chunk text didn't match the query embedding.

    Args:
        query: The search query text.
        category: Optional filter by category (Academic/Administrative/Educational).
        top_k: Number of results to return.
        threshold: Minimum cosine similarity score.

    Returns:
        List of dicts with keys: text, filename, category, score.
    """
    ensure_collection()
    client = get_qdrant_client()

    query_embedding = embed_texts([query])[0]

    # Build optional category filter
    search_filter = None
    if category:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=search_filter,
        limit=top_k,
    )

    # Filter by threshold and format
    hits: List[dict] = []
    seen_keys: set = set()  # (filename, chunk_index) for dedup
    for point in results.points:
        score = point.score
        if score >= threshold:
            payload = point.payload
            key = (payload.get("filename", ""), payload.get("chunk_index", 0))
            seen_keys.add(key)
            hits.append(
                {
                    "text": payload.get("text", ""),
                    "filename": payload.get("filename", ""),
                    "category": payload.get("category", ""),
                    "chunk_index": payload.get("chunk_index", 0),
                    "score": round(score, 4),
                }
            )

    # ── Pass 2: Filename-keyword boosting ──────────────────────
    query_keywords = _extract_filename_keywords(query)
    if query_keywords:
        # Scroll all unique filenames in the collection (lightweight payload-only scan)
        try:
            scroll_filter = search_filter  # respect the category filter
            all_points, _ = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=scroll_filter,
                limit=500,
                with_payload=["filename", "category"],
                with_vectors=False,
            )
            # Identify filenames that contain any query keyword
            matched_filenames: set = set()
            for pt in all_points:
                fname = (pt.payload.get("filename") or "").lower()
                # Match against the cleaned filename (no extension, underscores → spaces)
                fname_clean = fname.replace("_", " ").replace("-", " ").rsplit(".", 1)[0]
                for kw in query_keywords:
                    if kw in fname_clean:
                        matched_filenames.add(pt.payload.get("filename", ""))
                        break

            # For each matched filename, retrieve its chunks via vector search
            for mf in matched_filenames:
                fname_filter_conditions = [
                    FieldCondition(key="filename", match=MatchValue(value=mf)),
                ]
                if category:
                    fname_filter_conditions.append(
                        FieldCondition(key="category", match=MatchValue(value=category)),
                    )
                fname_results = client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_embedding,
                    query_filter=Filter(must=fname_filter_conditions),
                    limit=3,  # top chunks per matched file
                )
                for point in fname_results.points:
                    payload = point.payload
                    key = (payload.get("filename", ""), payload.get("chunk_index", 0))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        hits.append(
                            {
                                "text": payload.get("text", ""),
                                "filename": payload.get("filename", ""),
                                "category": payload.get("category", ""),
                                "chunk_index": payload.get("chunk_index", 0),
                                "score": round(point.score, 4),
                            }
                        )
        except Exception as exc:
            print(f"Filename-keyword boost pass failed (non-fatal): {exc}")

    # Sort all hits by score descending and return top_k
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:top_k]


# ── Delete ────────────────────────────────────────────────────
def delete_document(filename: str, category: Optional[str] = None):
    """Delete all chunks belonging to a specific document."""
    client = get_qdrant_client()

    must_conditions = [
        FieldCondition(key="filename", match=MatchValue(value=filename))
    ]
    if category:
        must_conditions.append(
            FieldCondition(key="category", match=MatchValue(value=category))
        )

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(must=must_conditions),
    )
    print(f"Deleted chunks for '{filename}' from Qdrant")


# ── Seed existing data files ──────────────────────────────────
def _get_indexed_filenames() -> set:
    """Return the set of filenames already indexed in Qdrant."""
    try:
        client = get_qdrant_client()
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=["filename"],
            with_vectors=False,
        )
        return {point.payload.get("filename", "") for point in result[0]}
    except Exception:
        return set()


def seed_existing_documents():
    """
    Index all existing .txt files from the data/ directory
    into Qdrant (if not already indexed).
    """
    from app.config import ACADEMIC_DIR, ADMINISTRATIVE_DIR, EDUCATIONAL_DIR

    dirs = {
        "Academic": ACADEMIC_DIR,
        "Administrative": ADMINISTRATIVE_DIR,
        "Educational": EDUCATIONAL_DIR,
    }

    total = 0
    already_indexed = _get_indexed_filenames()
    for category, dir_path in dirs.items():
        if not dir_path.exists():
            continue
        for txt_file in dir_path.glob("*.txt"):
            if txt_file.name in already_indexed:
                print(f"Skipping already indexed: '{txt_file.name}'")
                continue
            text = txt_file.read_text(encoding="utf-8")
            if text.strip():
                count, _ids = index_document(text, txt_file.name, category)
                total += count

    print(f"Seeded {total} total chunks from existing data files")
    return total
