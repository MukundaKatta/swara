"""Search index with TF-IDF scoring and inverted index."""
import math, re, time, logging, hashlib
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: str
    content: str
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    indexed_at: float = field(default_factory=time.time)

@dataclass
class SearchResult:
    doc_id: str
    score: float
    title: str
    snippet: str
    highlights: List[str] = field(default_factory=list)

class InvertedIndex:
    """TF-IDF based inverted index for full-text search."""

    def __init__(self):
        self._docs: Dict[str, Document] = {}
        self._index: Dict[str, Set[str]] = defaultdict(set)  # term -> doc_ids
        self._term_freq: Dict[str, Counter] = {}  # doc_id -> term counts
        self._doc_lengths: Dict[str, int] = {}

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()
        # Remove stopwords
        stops = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for",
                "of", "and", "or", "but", "not", "with", "this", "that", "it", "be", "as"}
        return [t for t in tokens if t not in stops and len(t) > 1]

    def add(self, doc: Document) -> None:
        self._docs[doc.id] = doc
        tokens = self._tokenize(doc.content + " " + doc.title)
        self._term_freq[doc.id] = Counter(tokens)
        self._doc_lengths[doc.id] = len(tokens)
        for term in set(tokens):
            self._index[term].add(doc.id)

    def add_many(self, docs: List[Document]) -> int:
        for doc in docs:
            self.add(doc)
        return len(docs)

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: Dict[str, float] = defaultdict(float)
        N = len(self._docs)

        for term in query_tokens:
            if term not in self._index:
                continue
            df = len(self._index[term])
            idf = math.log((N + 1) / (df + 1)) + 1

            for doc_id in self._index[term]:
                tf = self._term_freq[doc_id][term]
                doc_len = self._doc_lengths[doc_id]
                # BM25-like scoring
                k1, b = 1.5, 0.75
                avg_dl = sum(self._doc_lengths.values()) / max(1, N)
                tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / max(1, avg_dl)))
                scores[doc_id] += tf_norm * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for doc_id, score in ranked:
            doc = self._docs[doc_id]
            # Generate snippet around first match
            snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
            highlights = [t for t in query_tokens if t in self._term_freq.get(doc_id, {})]
            results.append(SearchResult(doc_id=doc_id, score=round(score, 4),
                                       title=doc.title, snippet=snippet, highlights=highlights))

        return results

    @property
    def stats(self) -> Dict:
        return {"documents": len(self._docs), "unique_terms": len(self._index),
                "avg_doc_length": round(sum(self._doc_lengths.values()) / max(1, len(self._docs)), 1)}
