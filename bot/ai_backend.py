"""AI backend abstraction — supports OpenAI API and Ollama."""

import logging
from abc import ABC, abstractmethod

import aiohttp
from openai import AsyncOpenAI

from .config import config

logger = logging.getLogger(__name__)


class AIBackend(ABC):
    """Abstract base class for AI backends."""

    @abstractmethod
    async def generate(self, messages: list[dict], system_prompt: str) -> str:
        """Generate a response given conversation messages."""
        ...


class OpenAIBackend(AIBackend):
    """OpenAI API backend (GPT-4o, GPT-4o-mini, etc.)."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model

    async def generate(self, messages: list[dict], system_prompt: str) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=2048,
                temperature=0.7,
            )
            return response.choices[0].message.content or "..."
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"⚠️ Ошибка AI: {type(e).__name__}. Попробуйте позже."


class OllamaBackend(AIBackend):
    """Ollama backend for local models."""

    def __init__(self):
        self.base_url = config.ollama_url
        self.model = config.ollama_model

    async def generate(self, messages: list[dict], system_prompt: str) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": False,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(f"Ollama error {resp.status}: {text}")
                        return "⚠️ Ошибка локальной модели. Проверьте, запущен ли Ollama."

                    data = await resp.json()
                    return data.get("message", {}).get("content", "...")
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection error: {e}")
            return "⚠️ Не удалось подключиться к Ollama. Убедитесь, что сервер запущен."


def get_backend() -> AIBackend:
    """Factory: create the configured AI backend."""
    if config.ai_backend == "ollama":
        return OllamaBackend()
    return OpenAIBackend()
