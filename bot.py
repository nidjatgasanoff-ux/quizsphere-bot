import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT_SHORTS = """Ты — эксперт по созданию вирусных квизов для YouTube Shorts о здоровье и питании.

Генерируй ровно 5 вопросов в формате JSON:

{
  "questions": [
    {
      "question": "Вопрос строго от 10 до 14 слов. Цепляющий и интересный.",
      "options": ["Вариант 3-5 слов", "Вариант 3-5 слов", "Вариант 3-5 слов", "Вариант 3-5 слов"],
      "correct_index": 0,
      "explanation": "Короткое полезное объяснение 2-4 предложения."
    }
  ]
}

Правила:
- Вопрос: 10-14 слов
- Варианты: 3-5 слов каждый
- Всегда 4 варианта
- Язык: русский"""

SYSTEM_PROMPT_LONG = """Ты — эксперт по квизам о здоровье.

Генерируй ровно 5 вопросов в формате JSON со структурой как выше."""

THEMES_RU = {
    "natural_health": "🌿 Натуральное здоровье",
    "vitamins_minerals": "💊 Витамины и минералы",
    "herbs_berries": "🫐 Травы и ягоды",
    "brain_nutrition": "🧠 Мозг и питание",
    "natural_foods": "🌍 Продукты мира",
    "hormones_food": "⚗️ Гормоны и еда",
    "plant_facts": "🌱 Факты о растениях",
    "superfoods": "⚡ Суперфуды",
    "sleep_health": "😴 Сон и здоровье",
    "gut_health": "🦠 Здоровье кишечника",
    "antioxidants": "🍇 Антиоксиданты",
    "immunity": "🛡️ Иммунитет",
    "skin_nutrition": "✨ Питание для кожи",
    "energy_foods": "⚡ Энергия и еда",
    "detox_foods": "🫧 Детокс продукты",
    "brain_foods": "🧠 Еда для мозга",
}

THEMES_EN = {
    "natural_health": "Natural Health Facts",
    "vitamins_minerals": "Vitamins and Minerals",
    "herbs_berries": "Herbs and Berries",
    "brain_nutrition": "Brain and Nutrition",
    "natural_foods": "Natural Foods Around The World",
    "hormones_food": "Hormones and Food",
    "plant_facts": "Amazing Plant Facts",
    "superfoods": "Superfoods",
    "sleep_health": "Sleep and Health",
    "gut_health": "Gut Health and Microbiome",
    "antioxidants": "Antioxidants and Free Radicals",
    "immunity": "Immunity Boosting Foods",
    "skin_nutrition": "Nutrition for Healthy Skin",
    "energy_foods": "Energy and Food",
    "detox_foods": "Natural Detox Foods",
    "brain_foods": "Brain Boosting Foods",
}


def format_quiz_result(raw_text: str) -> str:
    try:
        data = json.loads(raw_text.strip())
        questions = data.get("questions", [])
        result = []
        for i, q in enumerate(questions, 1):
            result.append(f"🔥 Вопрос {i}\n{q.get('question', '')}\n")
            options = q.get("options", [])
            correct = q.get("correct_index", 0)
            for idx, opt in enumerate(options):
                mark = "✅ " if idx == correct else ""
                letter = chr(65 + idx)
                result.append(f"{letter}) {mark}{opt}")
            result.append(f"\n💡 Объяснение: {q.get('explanation', '')}\n")
            result.append("─" * 35)
        return "\n".join(result)
    except Exception:
        return raw_text


def generate_quiz(theme_label: str, quiz_num: int, is_shorts: bool) -> str:
    prompt = SYSTEM_PROMPT_SHORTS if is_shorts else SYSTEM_PROMPT_LONG
    user_prompt = f'Generate Quiz #{quiz_num} on theme: "{theme_label}". Make it high quality.'

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2000,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60,
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


def get_theme_keyboard():
    return [
        [InlineKeyboardButton(THEMES_RU["natural_health"], callback_data="theme_natural_health"),
         InlineKeyboardButton(THEMES_RU["vitamins_minerals"], callback_data="theme_vitamins_minerals")],
        [InlineKeyboardButton(THEMES_RU["herbs_berries"], callback_data="theme_herbs_berries"),
         InlineKeyboardButton(THEMES_RU["brain_nutrition"], callback_data="theme_brain_nutrition")],
        [InlineKeyboardButton(THEMES_RU["natural_foods"], callback_data="theme_natural_foods"),
         InlineKeyboardButton(THEMES_RU["hormones_food"], callback_data="theme_hormones_food")],
        [InlineKeyboardButton(THEMES_RU["plant_facts"], callback_data="theme_plant_facts"),
         InlineKeyboardButton(THEMES_RU["superfoods"], callback_data="theme_superfoods")],
        [InlineKeyboardButton(THEMES_RU["sleep_health"], callback_data="theme_sleep_health"),
         InlineKeyboardButton(THEMES_RU["gut_health"], callback_data="theme_gut_health")],
        [InlineKeyboardButton(THEMES_RU["antioxidants"], callback_data="theme_antioxidants"),
         InlineKeyboardButton(THEMES_RU["immunity"], callback_data="theme_immunity")],
        [InlineKeyboardButton(THEMES_RU["skin_nutrition"], callback_data="theme_skin_nutrition"),
         InlineKeyboardButton(THEMES_RU["energy_foods"], callback_data="theme_energy_foods")],
        [InlineKeyboardButton(THEMES_RU["detox_foods"], callback_data="theme_detox_foods"),
         InlineKeyboardButton(THEMES_RU["brain_foods"], callback_data="theme_brain_foods")],
        [InlineKeyboardButton("✏️ Своя тема", callback_data="custom_theme")],
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я QuizSphere Bot 🌿\n\nНажми /quiz")


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Shorts (10-14 слов)", callback_data="format_shorts")],
        [InlineKeyboardButton("🎬 Long video", callback_data="format_long")],
    ]
    await update.message.reply_text("🎯 Выбери формат:", reply_markup=InlineKeyboardMarkup(keyboard))


async def format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_shorts = query.data == "format_shorts"
    context.user_data["is_shorts"] = is_shorts
    fmt = "📱 Shorts" if is_shorts else "🎬 Long"
    await query.edit_message_text(f"Формат: {fmt}\n\nВыбери тему:", reply_markup=InlineKeyboardMarkup(get_theme_keyboard()))


async def theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "custom_theme":
        context.user_data["waiting_for_theme"] = True
        await query.edit_message_text("✏️ Напиши свою тему:")
        return

    theme_key = query.data.replace("theme_", "")
    theme_ru = THEMES_RU.get(theme_key, "🌿 Натуральное здоровье")
    theme_en = THEMES_EN.get(theme_key, "Natural Health Facts")
    is_shorts = context.user_data.get("is_shorts", False)

    context.user_data["last_theme_ru"] = theme_ru
    context.user_data["last_theme_en"] = theme_en

    await query.edit_message_text(f"⏳ Генерирую на тему {theme_ru}...")

    quiz_num = context.bot_data.get("quiz_num", 1)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        raw = generate_quiz(theme_en, quiz_num, is_shorts)
        formatted = format_quiz_result(raw) if is_shorts else raw
        full_text = f"{'📱 SHORTS' if is_shorts else '🎬 LONG'} | Квиз #{quiz_num} — {theme_ru}\n\n{formatted}"
        await query.message.reply_text(full_text[:4000])

        keyboard = [
            [InlineKeyboardButton("🔄 Ещё", callback_data="repeat_theme")],
            [InlineKeyboardButton("🎯 Новая тема", callback_data="new_quiz")],
        ]
        await query.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await query.message.reply_text(f"❌ Ошибка: {str(e)[:500]}")


async def repeat_theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await theme_callback(update, context)


async def handle_custom_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_theme", False):
        return
    context.user_data["waiting_for_theme"] = False
    theme = update.message.text
    is_shorts = context.user_data.get("is_shorts", False)
    context.user_data["last_theme_ru"] = theme

    await update.message.reply_text(f"⏳ Генерирую на тему {theme}...")

    quiz_num = context.bot_data.get("quiz_num", 1)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        raw = generate_quiz(theme, quiz_num, is_shorts)
        formatted = format_quiz_result(raw) if is_shorts else raw
        full_text = f"{'📱 SHORTS' if is_shorts else '🎬 LONG'} | Квиз #{quiz_num} — {theme}\n\n{formatted}"
        await update.message.reply_text(full_text[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:500]}")


async def new_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await quiz_command(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(format_callback, pattern="^format_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^theme_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^custom_theme$"))
    app.add_handler(CallbackQueryHandler(repeat_theme_callback, pattern="^repeat_theme$"))
    app.add_handler(CallbackQueryHandler(new_quiz_callback, pattern="^new_quiz$"))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_custom_theme))
    print("✅ Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
