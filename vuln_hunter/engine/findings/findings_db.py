"""SQLite findings database."""
from __future__ import annotations
import json, time, uuid, os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import aiosqlite, structlog
logger = structlog.get_logger(__name__)

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Finding:
    id: str = ""
    title: str = ""
    severity: str = "info"
    category: str = ""
    target: str = ""
    description: str = ""
    evidence: list = None
    proof_of_concept: str = ""
    remediation: str = ""
    cvss_score: float = 0.0
    cvss_vector: str = ""
    refs: list = None
    tool: str = ""
    timestamp: float = 0
    false_positive: bool = False
    confirmed: bool = False
    def __post_init__(self):
        if self.evidence is None: self.evidence = []
        if self.refs is None: self.refs = []
        if self.timestamp == 0: self.timestamp = time.time()
    def to_dict(self): return asdict(self)

class FindingsDB:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY, title TEXT, severity TEXT, category TEXT,
        target TEXT, description TEXT, evidence TEXT, proof_of_concept TEXT,
        remediation TEXT, cvss_score REAL, cvss_vector TEXT, refs TEXT,
        tool TEXT, timestamp REAL, false_positive INTEGER, confirmed INTEGER
    );
    CREATE INDEX IF NOT EXISTS idx_sev ON findings(severity);
    """
    def __init__(self, db_path="results/findings.db"):
        self.db_path = db_path; self._db = None
    async def _db_conn(self):
        if self._db is None:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._db = await aiosqlite.connect(self.db_path)
            await self._db.executescript(self.SCHEMA)
            await self._db.commit()
        return self._db
    async def add(self, f: Finding) -> str:
        db = await self._db_conn()
        if not f.id: f.id = str(uuid.uuid4())[:12]
        await db.execute(
            "INSERT OR REPLACE INTO findings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f.id, f.title, f.severity, f.category, f.target, f.description,
             json.dumps(f.evidence), f.proof_of_concept, f.remediation,
             f.cvss_score, f.cvss_vector, json.dumps(f.refs), f.tool,
             f.timestamp, int(f.false_positive), int(f.confirmed)))
        await db.commit()
        return f.id
    async def list_all(self, severity=None, category=None, limit=1000):
        db = await self._db_conn()
        q = "SELECT * FROM findings WHERE 1=1"; params: list = []
        if severity: q += " AND severity = ?"; params.append(severity)
        if category: q += " AND category = ?"; params.append(category)
        q += " ORDER BY cvss_score DESC, timestamp DESC LIMIT ?"; params.append(limit)
        async with db.execute(q, params) as cur:
            rows = await cur.fetchall()
            return [self._row_to_finding(r) for r in rows]
    async def count(self, severity=None):
        db = await self._db_conn()
        q = "SELECT COUNT(*) FROM findings"; params: list = []
        if severity: q += " WHERE severity = ?"; params.append(severity)
        async with db.execute(q, params) as cur:
            r = await cur.fetchone()
            return r[0] if r else 0
    async def export(self, fmt="json"):
        findings = await self.list_all()
        path = f"results/findings.{fmt}"
        os.makedirs("results", exist_ok=True)
        if fmt == "json":
            with open(path, "w") as f:
                json.dump([fd.to_dict() for fd in findings], f, indent=2, default=str)
        return path
    async def close(self):
        if self._db: await self._db.close(); self._db = None
    def _row_to_finding(self, r):
        return Finding(id=r[0], title=r[1], severity=r[2], category=r[3], target=r[4],
            description=r[5], evidence=json.loads(r[6]), proof_of_concept=r[7],
            remediation=r[8], cvss_score=r[9], cvss_vector=r[10],
            refs=json.loads(r[11]), tool=r[12], timestamp=r[13],
            false_positive=bool(r[14]), confirmed=bool(r[15]))
