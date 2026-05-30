"""Telegram bot message handlers."""

import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from .config import config
from .ai_backend import get_backend
from .storage import add_message, get_context, clear_context, get_stats

logger = logging.getLogger(__name__)
router = Router()

ai = get_backend()


def is_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot."""
    if not config.allowed_users:
        return True
    return user_id in config.allowed_users


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    if not is_allowed(message.from_user.id):
        await message.answer("⛔ Доступ ограничен.")
        return

    await message.answer(
        "👋 Привет! Я AI-ассистент.\n\n"
        "Просто напиши мне сообщение, и я отвечу.\n\n"
        "Команды:\n"
        "/reset — очистить историю диалога\n"
        "/stats — статистика использования\n"
        "/help — справка"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    if not is_allowed(message.from_user.id):
        return

    await message.answer(
        "🤖 **AI-ассистент**\n\n"
        "Я могу помочь с:\n"
        "• Ответами на вопросы\n"
        "• Написанием текстов\n"
        "• Генерацией кода\n"
        "• Анализом информации\n"
        "• Переводом\n\n"
        "Просто напишите сообщение!\n\n"
        "Команды:\n"
        "/reset — начать диалог заново\n"
        "/stats — статистика\n",
        parse_mode="Markdown",
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    """Handle /reset command — clear conversation context."""
    if not is_allowed(message.from_user.id):
        return

    await clear_context(message.from_user.id)
    await message.answer("🔄 История диалога очищена. Начнём сначала!")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Handle /stats command."""
    if not is_allowed(message.from_user.id):
        return

    stats = await get_stats()
    await message.answer(
        f"📊 Статистика:\n"
        f"• Пользователей: {stats['total_users']}\n"
        f"• Сообщений: {stats['total_messages']}\n"
        f"• Бэкенд: {config.ai_backend}\n"
        f"• Модель: {config.openai_model if config.ai_backend == 'openai' else config.ollama_model}"
    )


@router.message(F.text)
async def handle_message(message: Message):
    """Handle regular text messages — send to AI."""
    user_id = message.from_user.id

    if not is_allowed(user_id):
        await message.answer("⛔ Доступ ограничен.")
        return

    user_text = message.text.strip()
    if not user_text:
        return

    # Show typing indicator
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Save user message
    await add_message(user_id, "user", user_text)

    # Get context
    context = await get_context(user_id, config.max_context_messages)

    # Generate AI response
    try:
        response = await ai.generate(context, config.system_prompt)
    except Exception as e:
        logger.error(f"AI generation error for user {user_id}: {e}")
        response = "⚠️ Произошла ошибка. Попробуйте позже."

    # Save assistant response
    await add_message(user_id, "assistant", response)

    # Send response (split if too long for Telegram)
    if len(response) <= 4096:
        await message.answer(response)
    else:
        # Split into chunks
        for i in range(0, len(response), 4096):
            await message.answer(response[i : i + 4096])

    logger.info(f"User {user_id}: {user_text[:50]}... -> {len(response)} chars")
