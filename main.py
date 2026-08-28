import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ---------- /start command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name

    welcome_text = (
        f"👋 Hi {user_first_name}!\n"
        f"Welcome to Football Analysis Bot ⚽📊\n\n"
        f"Here you'll find match breakdowns, team stats, and form analysis "
        f"for upcoming games.\n\n"
        f"What would you like to do?"
    )

    keyboard = [
        [InlineKeyboardButton("📊 View Today's Analysis", callback_data="today_analysis")],
        [InlineKeyboardButton("ℹ️ Learn More", callback_data="learn_more")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


# ---------- Today's Analysis ----------
async def today_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Replace this list with today's real matches/analysis
    matches = [
        {
            "match": "Arsenal vs Chelsea",
            "form": "Arsenal: WWDWL | Chelsea: LWWDW",
            "h2h": "Last 5 meetings: Arsenal 2W, Chelsea 2W, 1D",
            "stat": "Arsenal have scored in 8 of their last 10 home games"
        },
        {
            "match": "Man City vs Liverpool",
            "form": "Man City: WWWDW | Liverpool: WLWWD",
            "h2h": "Last 5 meetings: Man City 3W, Liverpool 2W",
            "stat": "Both teams have scored in 7 of the last 8 meetings"
        }
    ]

    text = "📊 *Today's Analysis*\n\n"
    for m in matches:
        text += (
            f"⚽ *{m['match']}*\n"
            f"Form: {m['form']}\n"
            f"H2H: {m['h2h']}\n"
            f"Key stat: {m['stat']}\n\n"
        )

    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ---------- Learn More ----------
async def learn_more_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "ℹ️ *About This Bot*\n\n"
        "Football match analysis and stats. Daily breakdowns of team form, "
        "head-to-head history, and key stats for upcoming matches."
    )

    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ---------- Back to main menu ----------
async def back_to_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_first_name = query.from_user.first_name

    welcome_text = (
        f"👋 Hi {user_first_name}!\n"
        f"Welcome to Football Analysis Bot ⚽📊\n\n"
        f"Here you'll find match breakdowns, team stats, and form analysis "
        f"for upcoming games.\n\n"
        f"What would you like to do?"
    )

    keyboard = [
        [InlineKeyboardButton("📊 View Today's Analysis", callback_data="today_analysis")],
        [InlineKeyboardButton("ℹ️ Learn More", callback_data="learn_more")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(welcome_text, reply_markup=reply_markup)


# ---------- Button router ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "today_analysis":
        await today_analysis_handler(update, context)
    elif data == "learn_more":
        await learn_more_handler(update, context)
    elif data == "back_to_menu":
        await back_to_menu_handler(update, context)


# ---------- Main entry point ----------
if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
