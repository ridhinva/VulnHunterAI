"""Campaign orchestrator."""
from __future__ import annotations
import asyncio, json, signal, time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import structlog
logger = structlog.get_logger(__name__)

class CampaignPhase(str, Enum):
    RECON="recon"; SCAN="scan"; CLASSIFY="classify"
    EXPLOIT="exploit"; REPORT="reporting"; COMPLETE="complete"

@dataclass
class CampaignState:
    target: str = ""; phase: str = ""; findings_count: int = 0
    cost: float = 0.0; start_time: float = field(default_factory=time.time)
    completed: bool = False

class Orchestrator:
    def __init__(self, provider=None, max_cost=50.0, output_dir="results"):
        self.provider = provider
        self.max_cost = max_cost
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._shutdown = asyncio.Event()

    async def run(self, target):
        logger.info("campaign_starting", target=target)
        state = CampaignState(target=target)
        phases = [CampaignPhase.RECON, CampaignPhase.SCAN,
                  CampaignPhase.CLASSIFY, CampaignPhase.EXPLOIT]
        for phase in phases:
            if self._shutdown.is_set(): break
            state.phase = phase.value
            logger.info("phase_start", phase=phase.value)
            await asyncio.sleep(0.01)
        state.completed = True
        logger.info("campaign_complete", findings=state.findings_count, cost=state.cost)
        return state

    def shutdown(self):
        self._shutdown.set()
