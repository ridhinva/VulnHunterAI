"""Swarm working memory."""
from __future__ import annotations
from typing import Any
class SwarmMemory:
    def __init__(self): self._data: dict[str, Any] = {}
    def set(self, k, v): self._data[k] = v
    def get(self, k, d=None): return self._data.get(k, d)
    def snapshot(self): return dict(self._data)
