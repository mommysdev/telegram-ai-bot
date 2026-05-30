"""Bot configuration from environment variables."""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Telegram
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))

    # AI Backend
    ai_backend: str = field(default_factory=lambda: os.getenv("AI_BACKEND", "openai"))

    # OpenAI
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    # Ollama
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:14b"))

    # Bot behavior
    system_prompt: str = field(
        default_factory=lambda: os.getenv(
            "SYSTEM_PROMPT", "Ты полезный AI-ассистент. Отвечай кратко и по делу."
        )
    )
    max_context_messages: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
    )

    # Access control
    allowed_users: list[int] = field(default_factory=list)

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    def __post_init__(self):
        raw_users = os.getenv("ALLOWED_USERS", "")
        if raw_users.strip():
            self.allowed_users = [int(uid.strip()) for uid in raw_users.split(",") if uid.strip()]
        else:
            self.allowed_users = []

        if not self.bot_token:
            raise ValueError("BOT_TOKEN is required. Set it in .env file.")


config = Config()
