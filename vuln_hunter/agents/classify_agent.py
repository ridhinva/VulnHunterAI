"""Classification: CVE matching, CVSS scoring."""
from __future__ import annotations
from vuln_hunter.agents.base import BaseAgent
class ClassifyAgent(BaseAgent):
    """Classification: CVE matching, CVSS scoring."""
    def get_system_prompt(self):
        return "You are a classify security specialist. Analyze findings and produce structured output."
    async def run(self, target, **kwargs):
        return {"agent": "classify", "target": target, "findings": []}
