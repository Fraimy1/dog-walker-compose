from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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
        [KeyboardButton(text=get_text("change_name_button", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


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
