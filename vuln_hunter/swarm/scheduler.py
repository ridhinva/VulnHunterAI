"""Swarm scheduler."""
from __future__ import annotations
from vuln_hunter.swarm.agent_base import SwarmAgent
from typing import Callable
class SwarmScheduler:
    def __init__(self, max_parallel=4):
        self._agents: list[tuple[str, SwarmAgent, Callable]] = []
        self._max_parallel = max_parallel
    def register(self, name, agent, callback):
        self._agents.append((name, agent, callback))
    async def run(self):
        for name, agent, cb in self._agents:
            if agent.should_run(): await cb()
