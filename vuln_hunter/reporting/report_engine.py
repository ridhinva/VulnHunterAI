"""Report generation."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import structlog, json
logger = structlog.get_logger(__name__)

class ReportEngine:
    def __init__(self, output_dir="results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    async def generate(self, state, fmt="markdown"):
        path = self.output_dir / f"report.{fmt}"
        if fmt == "markdown": path.write_text(self._md(state))
        elif fmt == "json": path.write_text(json.dumps({"target":state.target,"findings":[]}, indent=2))
        elif fmt == "html": path.write_text(self._html(state))
        elif fmt == "sarif": path.write_text(self._sarif(state))
        return str(path)
    def _md(self, s): return f"# VulnHunterAI Report\n\nTarget: {s.target}\n"
    def _html(self, s): return f"<html><body><h1>Report for {s.target}</h1></body></html>"
    def _sarif(self, s): return json.dumps({"version":"2.1.0","runs":[]})
