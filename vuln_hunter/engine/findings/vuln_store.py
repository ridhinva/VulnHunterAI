"""Vulnerability store."""
from __future__ import annotations
from dataclasses import dataclass, field
from vuln_hunter.engine.findings.findings_db import FindingsDB, Finding
@dataclass
class Vulnerability:
    cve_id: str=""; title: str=""; severity: str="info"; cvss_score: float=0.0
    description: str=""; references: list[str]=field(default_factory=list)
class VulnStore:
    def __init__(self, db_path="results/findings.db"):
        self._db = FindingsDB(db_path); self._vulns = {}
    async def add(self, v: Vulnerability) -> str:
        f = Finding(title=v.title, severity=v.severity, category="vulnerability",
            target=v.cve_id, description=v.description, cvss_score=v.cvss_score, references=v.references)
        fid = await self._db.add(f); self._vulns[fid] = v; return fid
    async def search(self, q: str) -> list:
        all_f = await self._db.list_all(); q = q.lower()
        return [f for f in all_f if q in f.title.lower() or q in f.description.lower()]
    async def count(self) -> int: return await self._db.count()
    async def close(self): await self._db.close()
