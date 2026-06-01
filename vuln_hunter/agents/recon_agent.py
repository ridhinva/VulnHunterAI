"""Reconnaissance: subdomains, ports, services, OSINT."""
from __future__ import annotations
from vuln_hunter.agents.base import BaseAgent
class ReconAgent(BaseAgent):
    """Reconnaissance: subdomains, ports, services, OSINT."""
    def get_system_prompt(self):
        return "You are a recon security specialist. Analyze findings and produce structured output."
    async def run(self, target, **kwargs):
        return {"agent": "recon", "target": target, "findings": []}
