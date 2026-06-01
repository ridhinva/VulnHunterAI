"""Reporting: multi-format reports."""
from __future__ import annotations
from vuln_hunter.agents.base import BaseAgent
class ReportAgent(BaseAgent):
    """Reporting: multi-format reports."""
    def get_system_prompt(self):
        return "You are a report security specialist. Analyze findings and produce structured output."
    async def run(self, target, **kwargs):
        return {"agent": "report", "target": target, "findings": []}
