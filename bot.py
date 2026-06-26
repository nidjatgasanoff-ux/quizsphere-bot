import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT_SHORTS = """SYSTEM_PROMPT_SHORTS = """You are an elite YouTube Shorts quiz creator specializing in health, nutrition, vitamins, brain health, longevity and healthy habits.

YOUR TASK:
Create EXACTLY 5 highly engaging quiz questions for YouTube Shorts.

STRICT RULES:

- Every question MUST contain BETWEEN 10 AND 14 words.
- Never write fewer than 10 words.
- Never write more than 14 words.
- Every question must immediately create curiosity.
- Start naturally with words like:
Which, What, Why, How, Did you know, Can you guess.

Answer options:

- Exactly 3 answers.
- Label them A), B), C).
- Every answer MUST contain 3-5 words.
- Only ONE answer is correct.
- Wrong answers should sound believable.

Explanation:

- One short sentence.
- Maximum 25 words.
- Explain why the answer is correct.
- Include one interesting health fact.

Safety:

- Never give medical advice.
- Never claim to cure diseases.
- Use wording like:
supports,
may help,
is associated with,
is known for,
traditionally used.

OUTPUT FORMAT:

[English question]
([Russian translation])

A) ...
B) ...
C) ...

Correct: A) ... - Explanation.
([Russian translation])

---

Generate exactly 5 questions.
Do not add introductions.
Start immediately with Question 1.
"""

SYSTEM_PROMPT_LONG = """You are a YouTube quiz creator about natural health and nutrition.

RULES:
- No medical advice, no disease treatment claims
- Use safe wording: supports, is associated with, is known for, contributes to, traditionally used
- Questions must be accurate, educational, and interesting

OUTPUT FORMAT - follow exactly:

[English question]
([Russian translation])
A) [option]
B) [option]
C) [option]
Correct: [A or B or C]) [answer] - [2-3 sentence explanation] ([Russian translation of answer and explanation])
---

Spread correct answers across A, B, C. Generate exactly 10 questions. Start immediately with question 1."""

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


def generate_quiz(theme_label: str, quiz_num: int, is_shorts: bool) -> str:
    prompt = SYSTEM_PROMPT_SHORTS if is_shorts else SYSTEM_PROMPT_LONG
    user_prompt = f"""
Generate Quiz #{quiz_num} about the topic "{theme_label}".

Create exactly 5 YouTube Shorts quiz questions.

Requirements:
- Every question MUST contain between 10 and 14 words.
- Every answer option MUST contain between 3 and 5 words.
- Questions must be surprising, curiosity-driven and highly engaging.
- Avoid repeating common facts.
- Make viewers want to guess before revealing the answer.
- Follow the system prompt exactly.
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 3000,
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
    await update.message.reply_text(
        "👋 Привет! Я QuizSphere Bot 🌿\n\n"
        "Генерирую квизы о натуральном здоровье и питании.\n\n"
        "Нажми /quiz чтобы начать!"
    )


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Shorts (короткие вопросы)", callback_data="format_shorts")],
        [InlineKeyboardButton("🎬 Long video (развёрнутые вопросы)", callback_data="format_long")],
    ]
    await update.message.reply_text(
        "🎯 Выбери формат видео:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_shorts = query.data == "format_shorts"
    context.user_data["is_shorts"] = is_shorts
    fmt = "📱 Shorts" if is_shorts else "🎬 Long video"
    await query.edit_message_text(
        f"Формат: {fmt}\n\n🎯 Теперь выбери тему:",
        reply_markup=InlineKeyboardMarkup(get_theme_keyboard())
    )


async def theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "custom_theme":
        context.user_data["waiting_for_theme"] = True
        await query.edit_message_text("✏️ Напиши свою тему!\n\nНапример: Animals, Space, History...")
        return

    theme_key = query.data.replace("theme_", "")
    theme_ru = THEMES_RU.get(theme_key, "🌿 Натуральное здоровье")
    theme_en = THEMES_EN.get(theme_key, "Natural Health Facts")
    is_shorts = context.user_data.get("is_shorts", False)

    context.user_data["last_theme_key"] = theme_key
    context.user_data["last_theme_ru"] = theme_ru
    context.user_data["last_theme_en"] = theme_en

    fmt = "📱 Shorts" if is_shorts else "🎬 Long video"
    await query.edit_message_text(f"⏳ Генерирую {fmt} квиз на тему {theme_ru}...\nЭто займёт около 10 секунд 🙏")

    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        result = generate_quiz(theme_en, quiz_num, is_shorts)
        fmt_label = "📱 SHORTS" if is_shorts else "🎬 LONG VIDEO"
        full_text = f"{fmt_label} | Квиз #{quiz_num} — {theme_ru}\n\n" + result

        if len(full_text) <= 4096:
            await query.message.reply_text(full_text)
        else:
            for chunk in [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]:
                await query.message.reply_text(chunk)

        keyboard = [
            [InlineKeyboardButton("🔄 Ещё по этой теме", callback_data="repeat_theme")],
            [InlineKeyboardButton("🎯 Выбрать другую тему", callback_data="new_quiz")],
        ]
        await query.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        await query.message.reply_text(f"❌ Ошибка. Попробуй ещё раз: /quiz\n\n{str(e)}")


async def repeat_theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    theme_ru = context.user_data.get("last_theme_ru", "🌿 Натуральное здоровье")
    theme_en = context.user_data.get("last_theme_en", "Natural Health Facts")
    is_shorts = context.user_data.get("is_shorts", False)

    fmt = "📱 Shorts" if is_shorts else "🎬 Long video"
    await query.edit_message_text(f"⏳ Генерирую ещё {fmt} квиз на тему {theme_ru}...\n🙏 Секунду!")

    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        result = generate_quiz(theme_en, quiz_num, is_shorts)
        fmt_label = "📱 SHORTS" if is_shorts else "🎬 LONG VIDEO"
        full_text = f"{fmt_label} | Квиз #{quiz_num} — {theme_ru}\n\n" + result

        if len(full_text) <= 4096:
            await query.message.reply_text(full_text)
        else:
            for chunk in [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]:
                await query.message.reply_text(chunk)

        keyboard = [
            [InlineKeyboardButton("🔄 Ещё по этой теме", callback_data="repeat_theme")],
            [InlineKeyboardButton("🎯 Выбрать другую тему", callback_data="new_quiz")],
        ]
        await query.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        await query.message.reply_text(f"❌ Ошибка. Попробуй ещё раз: /quiz\n\n{str(e)}")


async def handle_custom_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_theme"):
        return
    context.user_data["waiting_for_theme"] = False
    theme = update.message.text
    is_shorts = context.user_data.get("is_shorts", False)

    context.user_data["last_theme_ru"] = theme
    context.user_data["last_theme_en"] = theme

    fmt = "📱 Shorts" if is_shorts else "🎬 Long video"
    await update.message.reply_text(f"⏳ Генерирую {fmt} квиз на тему «{theme}»...\n🙏 Секунду!")

    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        result = generate_quiz(theme, quiz_num, is_shorts)
        fmt_label = "📱 SHORTS" if is_shorts else "🎬 LONG VIDEO"
        full_text = f"{fmt_label} | Квиз #{quiz_num} — {theme}\n\n" + result

        if len(full_text) <= 4096:
            await update.message.reply_text(full_text)
        else:
            for chunk in [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]:
                await update.message.reply_text(chunk)

        keyboard = [
            [InlineKeyboardButton("🔄 Ещё по этой теме", callback_data="repeat_theme")],
            [InlineKeyboardButton("🎯 Выбрать другую тему", callback_data="new_quiz")],
        ]
        await update.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка. Попробуй ещё раз: /quiz\n\n{str(e)}")


async def new_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📱 Shorts (короткие вопросы)", callback_data="format_shorts")],
        [InlineKeyboardButton("🎬 Long video (развёрнутые вопросы)", callback_data="format_long")],
    ]
    await query.edit_message_text(
        "🎯 Выбери формат видео:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(format_callback, pattern="^format_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^theme_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^custom_theme$"))
    app.add_handler(CallbackQueryHandler(repeat_theme_callback, pattern="^repeat_theme$"))
    app.add_handler(CallbackQueryHandler(new_quiz_callback, pattern="^new_quiz$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_theme))
    print("QuizSphere Bot запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
