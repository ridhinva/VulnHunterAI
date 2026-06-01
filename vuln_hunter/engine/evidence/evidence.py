"""Evidence capture."""
from __future__ import annotations
import json, time, uuid
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import structlog
logger = structlog.get_logger(__name__)

@dataclass
class Evidence:
    id: str=""; type: str=""; target: str=""; tool: str=""
    timestamp: float=0; content: Any=None; metadata: dict=None
    def __post_init__(self):
        if not self.id: self.id = str(uuid.uuid4())[:12]
        if self.timestamp == 0: self.timestamp = time.time()
        if self.metadata is None: self.metadata = {}
    def to_dict(self):
        return {"id":self.id,"type":self.type,"target":self.target,"tool":self.tool,
                "timestamp":self.timestamp,"content":self.content,"metadata":self.metadata}

class EvidenceCapture:
    def __init__(self, output_dir="results/evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._evidence: list[Evidence] = []
    def add(self, e: Evidence) -> str:
        self._evidence.append(e); return e.id
    def capture_http(self, target, data, tool=""):
        return self.add(Evidence(type="http",target=target,tool=tool,content=data))
    def capture_output(self, target, tool, output):
        return self.add(Evidence(type="command_output",target=target,tool=tool,content=output))
    def get_all(self) -> list[Evidence]: return self._evidence
    def export_json(self, filepath=None) -> str:
        filepath = filepath or str(self.output_dir/"evidence.json")
        with open(filepath,"w") as f: json.dump([e.to_dict() for e in self._evidence], f, indent=2, default=str)
        return filepath
