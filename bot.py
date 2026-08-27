import json
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "content.json")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- content storage ----------

DEFAULT_CONTENT = {
    "today_analysis": "No analysis has been posted yet. Please check back soon.",
    "about_text": (
        "This bot shares match analysis, statistics, and football predictions "
        "based on 7 years of experience in sports analysis.\n\n"
        "Content is informational only. Sports betting involves risk."
    ),
}


def load_content() -> dict:
    if not os.path.exists(DATA_FILE):
        save_content(DEFAULT_CONTENT)
        return dict(DEFAULT_CONTENT)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_content(content: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


# ---------- keyboard ----------

def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📈 View Today's Analysis", callback_data="show_analysis")],
        [InlineKeyboardButton("ℹ️ Learn More", callback_data="show_about")],
    ]
    return InlineKeyboardMarkup(buttons)


def back_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(buttons)


def welcome_text(first_name: str) -> str:
    return (
        f"👋 Hi {first_name}!\n"
        f"Welcome to Football Analysis Bot ⚽📊\n\n"
        f"Here you'll find match analysis, statistics, and football "
        f"predictions based on 7 years of experience.\n\n"
        f"What would you like to do?"
    )


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name or "there"
    await update.message.reply_text(welcome_text(name), reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    content = load_content()

    if query.data == "show_analysis":
        await query.edit_message_text(
            f"📈 *Today's Analysis*\n\n{content['today_analysis']}",
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif query.data == "show_about":
        await query.edit_message_text(
            f"ℹ️ *About this bot*\n\n{content['about_text']}",
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif query.data == "back_to_menu":
        name = query.from_user.first_name or "there"
        await query.edit_message_text(welcome_text(name), reply_markup=main_menu_keyboard())


async def set_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /setanalysis <text>"""
    new_text = " ".join(context.args).strip()
    if not new_text:
        await update.message.reply_text(
            "Usage: /setanalysis <your analysis text>\n\n"
            "Example:\n/setanalysis PSG vs Marseille - Over 2.5 goals looks likely based on recent form."
        )
        return

    content = load_content()
    content["today_analysis"] = new_text
    save_content(content)
    await update.message.reply_text("✅ Today's analysis has been updated.")


async def set_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Usage: /setabout <text>"""
    new_text = " ".join(context.args).strip()
    if not new_text:
        await update.message.reply_text("Usage: /setabout <your about text>")
        return

    content = load_content()
    content["about_text"] = new_text
    save_content(content)
    await update.message.reply_text("✅ The 'About' text has been updated.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I didn't recognize that command. Use /start to see the menu.")


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setanalysis", set_analysis))
    application.add_handler(CommandHandler("setabout", set_about))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("Bot started. Polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
