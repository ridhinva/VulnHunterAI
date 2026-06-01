"""Cleanup registry."""
from __future__ import annotations
import os, signal, shutil, tempfile
from pathlib import Path
from typing import Callable
import structlog
logger = structlog.get_logger(__name__)

class CleanupRegistry:
    def __init__(self):
        self._callbacks: list[tuple[str, Callable]] = []
        self._temp: list[Path] = []
        self._signals = False
    def register(self, name, cb): self._callbacks.append((name, cb))
    def register_temp(self, path): self._temp.append(Path(path))
    def execute_all(self):
        for name, cb in reversed(self._callbacks):
            try: cb()
            except Exception as e: logger.error("cleanup_fail", name=name, error=str(e))
        for p in self._temp:
            try:
                if p.exists(): p.unlink() if p.is_file() else shutil.rmtree(p, ignore_errors=True)
            except Exception: pass
    def register_signal_handlers(self):
        if self._signals: return
        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)
        self._signals = True
    def _handler(self, s, f):
        logger.info("signal", sig=s); self.execute_all(); os._exit(128+s)

def get_temp_dir(prefix="vulnhunter_") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))
