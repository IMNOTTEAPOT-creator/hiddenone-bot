import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8715624521:AAEiOBdlnXHzahpOaFuoONojLEtsHYyGJlA"

THEMES = {
    "Фрукты": ["Яблоко", "Банан", "Апельсин"],
    "Животные": ["Кот", "Собака", "Тигр"],
    "Еда": ["Пицца", "Бургер", "Суп"],
    "Страны": ["Франция", "Япония", "Бразилия"]
}

game = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Начать игру", callback_data="start")]]
    await update.message.reply_text(
        "👁 HiddenOne готов!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# кнопки
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # старт
    if data == "start":
    	keyboard = [
        	[InlineKeyboardButton("🎲 Библиотека тем", callback_data="library")]
    	]

    	await query.edit_message_text(
        	"🎮 Выбери действие:",
        	reply_markup=InlineKeyboardMarkup(keyboard)
    	)
    elif data == "library":
    	keyboard = [
        	[InlineKeyboardButton(t, callback_data=f"theme_{t}")]
        	for t in THEMES
    	]

    	keyboard.append([
        	InlineKeyboardButton("⬅ Назад", callback_data="back_start")
    	])

    	await query.edit_message_text(
        	"📚 Библиотека тем:",
        	reply_markup=InlineKeyboardMarkup(keyboard)
    	)

    elif data == "back_start":
    	keyboard = [
        	[InlineKeyboardButton("🎲 Библиотека тем", callback_data="library")]
    	]

    	await query.edit_message_text(
        	"🎮 Выбери действие:",
        	reply_markup=InlineKeyboardMarkup(keyboard)
    	)
# тема
    elif data.startswith("theme_"):
        game["theme"] = data.replace("theme_", "")

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"players_{i}")]
            for i in range(3, 11)
        ]

        await query.edit_message_text(
            "👥 Выбери количество игроков:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # игроки
    elif data.startswith("players_"):
        game["players"] = int(data.split("_")[1])

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"spies_{i}")]
            for i in range(1, min(4, game["players"]))
        ]

        await query.edit_message_text(
            "😈 Выбери количество шпионов:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # шпионы
    elif data.startswith("spies_"):
        game["spies"] = int(data.split("_")[1])

        game["word"] = random.choice(THEMES[game["theme"]])

        roles = ["spy"] * game["spies"] + ["player"] * (game["players"] - game["spies"])
        random.shuffle(roles)

        game["roles"] = roles
        game["current"] = 0

        keyboard = [[InlineKeyboardButton("👁 Показать роль", callback_data="show")]]

        await query.edit_message_text(
            f"👤 Игрок 1 из {game['players']}\nПередай телефон 📱",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # показать роль
    elif data == "show":
        i = game["current"]
        role = game["roles"][i]

        if role == "spy":
            text = "😈 ТЫ ШПИОН!"
        else:
            text = f"🎭 Тема: {game['theme']}\n🔤 Слово: {game['word']}"

        keyboard = [[InlineKeyboardButton("🙈 Скрыть", callback_data="hide")]]

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # скрыть
    elif data == "hide":
        game["current"] += 1

        # ИГРА ЗАКОНЧЕНА
        if game["current"] >= game["players"]:
            keyboard = [[InlineKeyboardButton("🔁 Перезапуск", callback_data="restart")]]

            await query.edit_message_text(
                "🎉 Игра закончена!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        i = game["current"] + 1
        keyboard = [[InlineKeyboardButton("👁 Показать роль", callback_data="show")]]

        await query.edit_message_text(
            f"👤 Игрок {i} из {game['players']}\nПередай телефон 📱",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # перезапуск
    elif data == "restart":
        game.clear()

        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"theme_{t}")]
            for t in THEMES
        ]

        await query.edit_message_text(
            "🎮 Новая игра!\nВыбери тему:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()