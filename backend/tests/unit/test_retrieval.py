"""FAISS retriever tests: exact cosine, top-k bounds, deterministic ties."""

import numpy as np
import pytest

from app.services.retrieval import FaissRetriever
from app.services.vectors import DIMENSION


def test_exact_vector_similarity_is_one():
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(5, DIMENSION)).astype(np.float32)
    retriever = FaissRetriever(vectors, [f"J00{i}" for i in range(5)])
    results = retriever.search(vectors[2], top_k=5)
    assert results[0][0] == "J002"
    assert results[0][1] == pytest.approx(1.0, abs=1e-4)


def test_top_k_capped_at_index_size():
    rng = np.random.default_rng(7)
    vectors = rng.normal(size=(3, DIMENSION)).astype(np.float32)
    retriever = FaissRetriever(vectors, ["A", "B", "C"])
    assert len(retriever.search(vectors[0], top_k=10)) == 3
    assert len(retriever.search(vectors[0], top_k=1)) == 1


def test_ordering_matches_manual_cosine():
    rng = np.random.default_rng(11)
    vectors = rng.normal(size=(8, DIMENSION)).astype(np.float32)
    query = rng.normal(size=DIMENSION).astype(np.float32)
    retriever = FaissRetriever(vectors, [f"K{i}" for i in range(8)])
    results = retriever.search(query, top_k=8)

    def cosine(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    expected = sorted(
        ((f"K{i}", cosine(query, vectors[i])) for i in range(8)),
        key=lambda pair: (-pair[1], pair[0]),
    )
    assert [key for key, _ in results] == [key for key, _ in expected]
    for (_, got), (_, want) in zip(results, expected, strict=True):
        assert abs(got - want) < 1e-5


def test_identical_vectors_tie_broken_by_id():
    base = np.zeros(DIMENSION, dtype=np.float32)
    base[0] = 1.0
    same = base.copy()
    same[1] = 1.0  # identical rows -> cosine ties
    retriever = FaissRetriever(np.stack([same, base]), ["Z9", "A1"])
    results = retriever.search(base, top_k=2)
    # equal similarity: "A1" first (id order), deterministic across runs
    assert [key for key, _ in results] == ["A1", "Z9"]
    second = retriever.search(base, top_k=2)
    assert results == second
