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
ADMIN_ID = os.getenv("ADMIN_ID")  # your numeric Telegram user id, as a string
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


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name or "there"
    text = (
        f"👋 Hi {user_first_name}!\n"
        f"Welcome to Football Analysis Bot ⚽📊\n\n"
        f"Here you'll find match analysis, statistics, and football "
        f"predictions based on 7 years of experience.\n\n"
        f"What would you like to do?"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


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
        user_first_name = query.from_user.first_name or "there"
        text = (
            f"👋 Hi {user_first_name}!\n"
            f"Welcome to Football Analysis Bot ⚽📊\n\n"
            f"Here you'll find match analysis, statistics, and football "
            f"predictions based on 7 years of experience.\n\n"
            f"What would you like to do?"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())


async def is_admin(update: Update) -> bool:
    if not ADMIN_ID:
        return False
    return str(update.effective_user.id) == str(ADMIN_ID)


async def set_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin-only. Usage: /setanalysis <text> """
    if not await is_admin(update):
        await update.message.reply_text("This command is only available to the bot admin.")
