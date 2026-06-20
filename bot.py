import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a content creator for a YouTube quiz channel about natural health and nutrition.

RULES:
- No medical advice, no disease treatment claims
- Use safe wording: supports, is associated with, is known for, contributes to, traditionally used
- Questions must be accurate, educational, and YouTube monetization safe

CATEGORY MIX (10 questions total):
- 3 questions: Natural Foods (fruits, vegetables, nuts, seeds, oils)
- 3 questions: Vitamins and Minerals (zinc, magnesium, iodine, omega-3, vitamin C, selenium)
- 2 questions: Hormones and Brain Chemicals (serotonin, dopamine, melatonin)
- 2 questions: Herbs, Berries and Plants (chamomile, peppermint, blueberry, cranberry)

OUTPUT FORMAT - follow exactly for each question:

[English question]
([Russian translation])
A) [option]
B) [option]
C) [option]
Correct: [A or B or C]) [answer text] ([Russian translation])
---

Spread correct answers: use A about 3-4 times, B about 3-4 times, C about 2-3 times.
Generate exactly 10 questions. Start immediately with question 1, no intro text."""

THEMES = {
    "natural_health": "Natural Health Facts",
    "vitamins_minerals": "Vitamins and Minerals",
    "herbs_berries": "Herbs and Berries",
    "brain_nutrition": "Brain and Nutrition",
    "natural_foods": "Natural Foods Around The World",
    "hormones_food": "Hormones and Food",
    "plant_facts": "Amazing Plant Facts",
    "superfoods": "Superfoods",
}

THEMES_RU = {
    "natural_health": "🌿 Натуральное здоровье",
    "vitamins_minerals": "💊 Витамины и минералы",
    "herbs_berries": "🫐 Травы и ягоды",
    "brain_nutrition": "🧠 Мозг и питание",
    "natural_foods": "🌍 Продукты мира",
    "hormones_food": "⚗️ Гормоны и еда",
    "plant_facts": "🌱 Факты о растениях",
    "superfoods": "⚡ Суперфуды",
}


def generate_quiz(theme_key: str, quiz_num: int) -> str:
    theme_label = THEMES.get(theme_key, "Natural Health Facts")
    user_prompt = f'Generate Quiz #{quiz_num} on theme: "{theme_label}". Mix all 4 categories. Make questions surprising and educational. Spread correct answers across A, B, C positions.'

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 2000,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=60,
    )
    data = response.json()
    return data["content"][0]["text"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я QuizSphere Bot 🌿\n\n"
        "Генерирую квизы о натуральном здоровье и питании для твоего YouTube-канала.\n\n"
        "Нажми /quiz чтобы выбрать тему и создать квиз!"
    )


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(THEMES_RU["natural_health"], callback_data="theme_natural_health")],
        [InlineKeyboardButton(THEMES_RU["vitamins_minerals"], callback_data="theme_vitamins_minerals")],
        [InlineKeyboardButton(THEMES_RU["herbs_berries"], callback_data="theme_herbs_berries")],
        [InlineKeyboardButton(THEMES_RU["brain_nutrition"], callback_data="theme_brain_nutrition")],
        [InlineKeyboardButton(THEMES_RU["natural_foods"], callback_data="theme_natural_foods")],
        [InlineKeyboardButton(THEMES_RU["hormones_food"], callback_data="theme_hormones_food")],
        [InlineKeyboardButton(THEMES_RU["plant_facts"], callback_data="theme_plant_facts")],
        [InlineKeyboardButton(THEMES_RU["superfoods"], callback_data="theme_superfoods")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 Выбери тему квиза:", reply_markup=reply_markup)


async def theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    theme_key = query.data.replace("theme_", "")
    theme_ru = THEMES_RU.get(theme_key, "🌿 Натуральное здоровье")

    await query.edit_message_text(
        f"⏳ Генерирую квиз на тему {theme_ru}...\nЭто займёт около 20 секунд 🙏"
    )

    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        result = generate_quiz(theme_key, quiz_num)
        header = f"Квиз #{quiz_num} — {theme_ru}\n\n"
        full_text = header + result

        if len(full_text) <= 4096:
            await query.message.reply_text(full_text)
        else:
            chunks = [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]
            for chunk in chunks:
                await query.message.reply_text(chunk)

        keyboard = [[InlineKeyboardButton("🔄 Создать ещё квиз", callback_data="new_quiz")]]
        await query.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        await query.message.reply_text(
            f"❌ Ошибка при генерации. Попробуй ещё раз: /quiz\n\n{str(e)}"
        )


async def new_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(THEMES_RU["natural_health"], callback_data="theme_natural_health")],
        [InlineKeyboardButton(THEMES_RU["vitamins_minerals"], callback_data="theme_vitamins_minerals")],
        [InlineKeyboardButton(THEMES_RU["herbs_berries"], callback_data="theme_herbs_berries")],
        [InlineKeyboardButton(THEMES_RU["brain_nutrition"], callback_data="theme_brain_nutrition")],
        [InlineKeyboardButton(THEMES_RU["natural_foods"], callback_data="theme_natural_foods")],
        [InlineKeyboardButton(THEMES_RU["hormones_food"], callback_data="theme_hormones_food")],
        [InlineKeyboardButton(THEMES_RU["plant_facts"], callback_data="theme_plant_facts")],
        [InlineKeyboardButton(THEMES_RU["superfoods"], callback_data="theme_superfoods")],
    ]
    await query.edit_message_text(
        "🎯 Выбери тему квиза:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^theme_"))
    app.add_handler(CallbackQueryHandler(new_quiz_callback, pattern="^new_quiz$"))
    print("QuizSphere Bot запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
