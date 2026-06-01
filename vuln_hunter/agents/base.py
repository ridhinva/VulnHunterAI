"""Base agent with ReAct loop."""
from __future__ import annotations
from typing import Any
import structlog
logger = structlog.get_logger(__name__)
class BaseAgent:
    def __init__(self, provider=None): self.provider = provider
    async def think(self, ctx): return "thinking..."
    async def act(self, action, target): return {"result": "ok"}
    async def observe(self, result): return result
    async def react_loop(self, ctx, max_iter=10):
        for _ in range(max_iter):
            thought = await self.think(ctx)
            action = await self.act(thought, ctx)
            obs = await self.observe(action)
            if await self.is_done(obs): return obs
        return {"status": "max_iterations"}
    async def is_done(self, obs): return False
    def get_system_prompt(self): return "You are a security testing assistant."
