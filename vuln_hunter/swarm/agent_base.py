"""Base swarm agent."""
from __future__ import annotations
from vuln_hunter.swarm.blackboard import Blackboard, FindingType
class SwarmAgent:
    trigger_predicate = ""
    def __init__(self, blackboard: Blackboard): self.blackboard = blackboard
    def should_run(self) -> bool:
        if not self.trigger_predicate: return True
        ft = FindingType(self.trigger_predicate)
        return len(self.blackboard.get_findings(ft)) > 0
    async def run(self): raise NotImplementedError
