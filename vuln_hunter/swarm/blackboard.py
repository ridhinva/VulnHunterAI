"""Stigmergic shared blackboard."""
from __future__ import annotations
import time, math, uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List

HALF_LIVES = {
    "SUBDOMAIN": 21600, "PORT_OPEN": 21600, "HTTP_ENDPOINT": 7200,
    "TECHNOLOGY": 7200, "CVE_MATCH": 7200, "MISCONFIGURATION": 3600,
    "EXPLOIT_CHAIN": 3600, "EXPLOIT_RESULT": 1800, "CREDENTIAL": 900,
    "VULNERABILITY": 14400,
}

class FindingType(str, Enum):
    SUBDOMAIN = "subdomain"
    PORT_OPEN = "port_open"
    HTTP_ENDPOINT = "http_endpoint"
    TECHNOLOGY = "technology"
    CVE_MATCH = "cve_match"
    MISCONFIGURATION = "misconfiguration"
    EXPLOIT_CHAIN = "exploit_chain"
    EXPLOIT_RESULT = "exploit_result"
    CREDENTIAL = "credential"
    VULNERABILITY = "vulnerability"

@dataclass
class Finding:
    id: str = ""
    type: str = ""
    data: Any = None
    pheromone: float = 0.5
    created_at: float = field(default_factory=time.time)
    agent: str = ""

class Blackboard:
    def __init__(self):
        self._findings: list[Finding] = []

    def add_finding(self, finding_type, data, pheromone=0.5, agent=""):
        ft = finding_type.value if isinstance(finding_type, Enum) else str(finding_type)
        f = Finding(id=str(uuid.uuid4())[:12], type=ft, data=data, pheromone=pheromone, agent=agent)
        self._findings.append(f)
        return f

    def get_findings(self, finding_type=None, min_pheromone=0.0):
        results = self._findings
        if finding_type:
            ft = finding_type.value if isinstance(finding_type, Enum) else str(finding_type)
            results = [f for f in results if f.type == ft]
        return [f for f in results if f.pheromone >= min_pheromone]

    def get_hot_findings(self, limit=10):
        self.decay_pheromones()
        return sorted(self._findings, key=lambda f: f.pheromone, reverse=True)[:limit]

    def decay_pheromones(self, elapsed_seconds=300):
        for f in self._findings:
            hl = HALF_LIVES.get(f.type, 3600)
            f.pheromone *= math.exp(-0.693 * elapsed_seconds / hl)
        self._findings = [f for f in self._findings if f.pheromone > 0.01]

    def clear(self):
        self._findings.clear()
