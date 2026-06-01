"""Finding deduplication."""
from __future__ import annotations
import hashlib, json
class Deduplicator:
    def __init__(self): self._seen = set()
    def is_duplicate(self, data):
        h = self._hash(data)
        if h in self._seen: return True
        self._seen.add(h); return False
    def add(self, data): self._seen.add(self._hash(data))
    def clear(self): self._seen.clear()
    @staticmethod
    def _hash(data):
        n = json.dumps(data, sort_keys=True, default=str) if not isinstance(data, str) else data.strip().lower()
        return hashlib.sha256(n.encode()).hexdigest()[:16]
