import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT_SHORTS = """Ты — эксперт по вирусным квизам для YouTube Shorts и Telegram о здоровье и питании.

Генерируй **ровно 5 вопросов** в формате JSON:

{
  "questions": [
    {
      "question": "Вопрос строго 10-14 слов. Цепляющий, интересный, начинающийся с Какой, Что, Почему, Как и т.д.",
      "options": ["Вариант 3-5 слов", "Вариант 3-5 слов", "Вариант 3-5 слов", "Вариант 3-5 слов"],
      "correct_index": 0,
      "explanation": "Короткое, но полезное объяснение 2-4 предложения с фактами."
    }
  ]
}

Правила:
- Вопрос всегда 10-14 слов
- Каждый вариант — 3-5 слов
- Всегда 4 варианта
- Язык — русский, живой
- Без лечения болезней, используй мягкие слова: способствует, поддерживает, известен тем что...
- Генерируй только JSON, ничего больше."""

SYSTEM_PROMPT_LONG = """Генерируй 5 вопросов о здоровье в формате JSON как выше, но вопросы длиннее."""

THEMES_RU = {
    "natural_health": "🌿 Натуральное здоровье",
    "vitamins_minerals": "💊 Витамины и минералы",
}

THEMES_EN = {
    "natural_health": "Natural Health",
    "vitamins_minerals": "Vitamins and Minerals",
}

def get_theme_keyboard():
    return [
        [InlineKeyboardButton(THEMES_RU["natural_health"], callback_data="theme_natural_health")],
        [InlineKeyboardButton(THEMES_RU["vitamins_minerals"], callback_data="theme_vitamins_minerals")],
        [InlineKeyboardButton("✏️ Своя тема", callback_data="custom_theme")],
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! /quiz чтобы начать")

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Shorts", callback_data="format_shorts")],
        [InlineKeyboardButton("🎬 Long", callback_data="format_long")],
    ]
    await update.message.reply_text("Выбери формат:", reply_markup=InlineKeyboardMarkup(keyboard))

async def format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_shorts = query.data == "format_shorts"
    context.user_data["is_shorts"] = is_shorts
    await query.edit_message_text("Выбери тему:", reply_markup=InlineKeyboardMarkup(get_theme_keyboard()))

async def theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "custom_theme":
        context.user_data["waiting_for_theme"] = True
        await query.edit_message_text("Напиши тему:")
        return
    await query.edit_message_text("Генерирую...")

async def handle_custom_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_theme"):
        return
    context.user_data["waiting_for_theme"] = False
    await update.message.reply_text("Генерирую...")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(format_callback, pattern="^format_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^theme_|^custom_theme$"))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_custom_theme))
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
