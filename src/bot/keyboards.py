from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from src.bot.config import settings
from src.bot.i18n import get_text


def language_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for language selection."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇷🇺 Русский"),
                KeyboardButton(text="🇬🇧 English"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Main keyboard with walk buttons."""
    rows = [
        [KeyboardButton(text=get_text("walk_button", lang))],
        [KeyboardButton(text=get_text("walk_at_time_button", lang))],
        [KeyboardButton(text=get_text("ask_walk_button", lang))],
        [KeyboardButton(text=get_text("change_name_button", lang))],
    ]
    if settings.webapp_url:
        rows.append([
            KeyboardButton(
                text=get_text("stats_button", lang),
                web_app=WebAppInfo(url=settings.webapp_url),
            )
        ])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def ask_walk_keyboard(users: list, lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline keyboard for selecting who receives the walk request."""
    buttons = [
        [InlineKeyboardButton(text=get_text("ask_walk_all", lang), callback_data="ask_walk:all")]
    ]
    for user in users:
        name = user.display_name or user.username or f"User {user.telegram_id}"
        buttons.append([
            InlineKeyboardButton(text=name, callback_data=f"ask_walk:{user.telegram_id}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def parameter_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Keyboard for selecting walk parameters."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("didnt_poop", lang)),
                KeyboardButton(text=get_text("long_walk", lang)),
            ],
            [
                KeyboardButton(text=get_text("send", lang)),
                KeyboardButton(text=get_text("cancel", lang)),
            ],
        ],
        resize_keyboard=True,
    )
