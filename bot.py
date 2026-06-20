import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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


def generate_quiz(theme_label: str, quiz_num: int) -> str:
    user_prompt = f'Generate Quiz #{quiz_num} on theme: "{theme_label}". Mix all 4 categories. Make questions surprising and educational.'

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 2000,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60,
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я QuizSphere Bot 🌿\n\n"
        "Генерирую квизы о натуральном здоровье и питании.\n\n"
        "Нажми /quiz чтобы выбрать тему\n"
        "Или напиши /custom чтобы задать свою тему!"
    )


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 Выбери тему квиза:", reply_markup=reply_markup)


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_for_theme"] = True
    await update.message.reply_text(
        "✏️ Напиши свою тему для квиза!\n\n"
        "Например: Animals, Space, History, Ancient Rome..."
    )


async def handle_custom_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_theme"):
        return
    context.user_data["waiting_for_theme"] = False
    theme = update.message.text
    await update.message.reply_text(f"⏳ Генерирую квиз на тему «{theme}»...\nЭто займёт около 10 секунд 🙏")
    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1
    try:
        result = generate_quiz(theme, quiz_num)
        full_text = f"Квиз #{quiz_num} — {theme}\n\n" + result
        if len(full_text) <= 4096:
            await update.message.reply_text(full_text)
        else:
            for chunk in [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]:
                await update.message.reply_text(chunk)
        keyboard = [[InlineKeyboardButton("🔄 Создать ещё квиз", callback_data="new_quiz")]]
        await update.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка. Попробуй ещё раз: /quiz\n\n{str(e)}")


async def theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "custom_theme":
        context.user_data["waiting_for_theme"] = True
        await query.edit_message_text("✏️ Напиши свою тему для квиза!\n\nНапример: Animals, Space, History...")
        return

    theme_key = query.data.replace("theme_", "")
    theme_ru = THEMES_RU.get(theme_key, "🌿 Натуральное здоровье")
    theme_en = THEMES_EN.get(theme_key, "Natural Health Facts")

    await query.edit_message_text(f"⏳ Генерирую квиз на тему {theme_ru}...\nЭто займёт около 10 секунд 🙏")

    quiz_num = context.bot_data.get("quiz_num", 11)
    context.bot_data["quiz_num"] = quiz_num + 1

    try:
        result = generate_quiz(theme_en, quiz_num)
        full_text = f"Квиз #{quiz_num} — {theme_ru}\n\n" + result
        if len(full_text) <= 4096:
            await query.message.reply_text(full_text)
        else:
            for chunk in [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]:
                await query.message.reply_text(chunk)
        keyboard = [[InlineKeyboardButton("🔄 Создать ещё квиз", callback_data="new_quiz")]]
        await query.message.reply_text("✅ Готово!", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await query.message.reply_text(f"❌ Ошибка. Попробуй ещё раз: /quiz\n\n{str(e)}")


async def new_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
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
    await query.edit_message_text("🎯 Выбери тему квиза:", reply_markup=InlineKeyboardMarkup(keyboard))


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^theme_"))
    app.add_handler(CallbackQueryHandler(theme_callback, pattern="^custom_theme$"))
    app.add_handler(CallbackQueryHandler(new_quiz_callback, pattern="^new_quiz$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_theme))
    print("QuizSphere Bot запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
