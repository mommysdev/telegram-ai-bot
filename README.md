# 🤖 AI Telegram Bot — Шаблон

Универсальный Telegram-бот с интеграцией AI (OpenAI API / локальные модели).
Готов к деплою, легко кастомизируется под задачи клиента.

## Возможности
- 💬 Диалог с AI (GPT-4o / локальная модель через Ollama)
- 📝 Контекст беседы (помнит историю диалога)
- 👥 Мультипользовательский (каждый пользователь — отдельный контекст)
- ⚙️ Настраиваемый системный промпт (персонаж, роль, ограничения)
- 🔒 Whitelist пользователей (опционально)
- 📊 Логирование запросов
- 🐳 Docker-ready

## Стек
- Python 3.11+
- aiogram 3.x (асинхронный Telegram Bot API)
- OpenAI API / Ollama (переключаемый бэкенд)
- SQLite (хранение контекста)
- Docker + docker-compose

## Быстрый старт

```bash
# 1. Клонировать
git clone https://github.com/YOUR_USERNAME/telegram-ai-bot.git
cd telegram-ai-bot

# 2. Настроить
cp .env.example .env
# Заполнить BOT_TOKEN и OPENAI_API_KEY в .env

# 3. Запустить
docker-compose up -d
```

## Конфигурация (.env)
```
BOT_TOKEN=your_telegram_bot_token
AI_BACKEND=openai          # openai или ollama
OPENAI_API_KEY=sk-...      # для OpenAI
OPENAI_MODEL=gpt-4o-mini   # модель OpenAI
OLLAMA_URL=http://localhost:11434  # для Ollama
OLLAMA_MODEL=qwen2.5:14b   # модель Ollama
SYSTEM_PROMPT=Ты полезный AI-ассистент.
MAX_CONTEXT_MESSAGES=20
ALLOWED_USERS=              # пусто = все, или ID через запятую
```

## Структура проекта
```
├── bot/
│   ├── __init__.py
│   ├── main.py           # Точка входа
│   ├── config.py         # Конфигурация из .env
│   ├── handlers.py       # Обработчики сообщений
│   ├── ai_backend.py     # Абстракция AI (OpenAI/Ollama)
│   └── storage.py        # Хранение контекста (SQLite)
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Кастомизация для клиентов
- Изменить системный промпт → бот становится экспертом в любой области
- Добавить команды → /help, /reset, /settings
- Подключить базу знаний → RAG через embeddings
- Интеграция с CRM/сервисами → webhooks, API
- Оплата/подписка → интеграция с ЮKassa/Stripe

## Лицензия
MIT
