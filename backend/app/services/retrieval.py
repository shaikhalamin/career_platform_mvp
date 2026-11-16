"""In-memory cosine-similarity retrieval over FAISS (faiss-cpu).

An `IndexFlatIP` (inner product) over L2-normalized vectors is exact cosine
similarity — at 50 opportunities there is no approximation involved. The
index is rebuilt whenever the opportunity set changes (see the version-keyed
cache in `recommender.py`); searches themselves never touch the database.
"""

import logging

import faiss
import numpy as np

from app.services.vectors import DIMENSION

logger = logging.getLogger("app.services.retrieval")


class FaissRetriever:
    """Cosine-similarity top-K retriever over opportunity vectors."""

    def __init__(self, vectors: np.ndarray, keys: list[str]) -> None:
        """Build the index from a (n, DIMENSION) float32 matrix and the
        stable keys (opportunity ids) aligned with its rows."""
        if len(vectors) != len(keys):
            raise ValueError(f"vectors ({len(vectors)}) and keys ({len(keys)}) misaligned")
        if len(vectors) == 0:
            raise ValueError("cannot build a retriever over an empty opportunity set")
        matrix = np.ascontiguousarray(vectors.astype(np.float32))
        if matrix.ndim != 2 or matrix.shape[1] != DIMENSION:
            raise ValueError(f"expected (n, {DIMENSION}) matrix, got {matrix.shape}")
        faiss.normalize_L2(matrix)
        self._keys = list(keys)
        self._index = faiss.IndexFlatIP(DIMENSION)
        self._index.add(matrix)
        logger.debug("FAISS index built: %d vectors, dim=%d", self._index.ntotal, DIMENSION)

    @property
    def size(self) -> int:
        return self._index.ntotal

    def search(self, query: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        """Return [(opportunity_id, cosine_similarity)] best-first.

        Ties are broken deterministically by opportunity id so scores and
        rankings are reproducible across runs.
        """
        query_matrix = np.ascontiguousarray(query.astype(np.float32).reshape(1, -1))
        faiss.normalize_L2(query_matrix)
        k = min(max(1, top_k), self._index.ntotal)
        similarities, positions = self._index.search(query_matrix, k)
        results = [
            (self._keys[position], float(similarity))
            for similarity, position in zip(similarities[0], positions[0], strict=True)
            if position != -1
        ]
        # FAISS returns inner-product neighbours in descending similarity,
        # but its tie order is an implementation detail — re-sort for
        # stable, reproducible rankings.
        results.sort(key=lambda item: (-item[1], item[0]))
        return results
