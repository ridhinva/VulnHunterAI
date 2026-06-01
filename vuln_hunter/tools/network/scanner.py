"""network scanner orchestrator."""
from __future__ import annotations
from typing import Any
from vuln_hunter.tools.registry import get_registry
class NetworkScanner:
    def __init__(self): self.registry = get_registry()
    async def run_all(self, target):
        results = {}
        for tool in self.registry.list_tools("network", installed_only=True):
            results[tool.name] = await self.registry.execute(tool.name, target)
        return results
