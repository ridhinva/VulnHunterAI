"""Unified LLM Provider."""
from __future__ import annotations
from enum import Enum
from typing import Any, Optional
import structlog
logger = structlog.get_logger(__name__)

class ProviderType(str, Enum):
    OPENROUTER = "openrouter"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    LITELLM = "litellm"

class _Usage:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.cost = 0.0

class LLMProvider:
    def __init__(self, provider_type=ProviderType.OPENROUTER, api_key="",
                 model="openrouter/owl-alpha", base_url="https://openrouter.ai/api/v1",
                 max_tokens=8192, temperature=0.1):
        self.provider_type = provider_type
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None
        self._usage = _Usage()

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key or "none", base_url=self.base_url)
        return self._client

    async def complete(self, messages, tools=None):
        client = self._get_client()
        kwargs = {"model": self.model, "messages": messages,
                  "max_tokens": self.max_tokens, "temperature": self.temperature}
        if tools: kwargs["tools"] = tools
        try:
            resp = await client.chat.completions.create(**kwargs)
            return {"content": resp.choices[0].message.content, "usage": resp.usage}
        except Exception as e:
            logger.error("llm_error", error=str(e))
            return {"error": str(e)}

    async def stream(self, messages):
        client = self._get_client()
        stream = await client.chat.completions.create(
            model=self.model, messages=messages, stream=True)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def count_tokens(self, text):
        return len(text) // 4

    def estimate_cost(self, prompt_tokens, completion_tokens):
        rates = {"openrouter/owl-alpha": (0,0), "claude-sonnet-4-20250514": (3e-6, 15e-6)}
        rate = rates.get(self.model, (1e-6, 2e-6))
        return prompt_tokens * rate[0] + completion_tokens * rate[1]

    def reset_cost_tracking(self):
        self._usage = _Usage()
