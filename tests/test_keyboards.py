"""Tests for keyboard builders."""
from types import SimpleNamespace

import pytest

from src.bot.keyboards import ask_walk_keyboard, main_keyboard, parameter_keyboard


def make_user(display_name=None, username=None, telegram_id=12345):
    return SimpleNamespace(display_name=display_name, username=username, telegram_id=telegram_id)


# ---------------------------------------------------------------------------
# ask_walk_keyboard
# ---------------------------------------------------------------------------

def test_ask_walk_keyboard_empty_users():
    kb = ask_walk_keyboard([], "en")
    # Only the "Everyone" row
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].callback_data == "ask_walk:all"


def test_ask_walk_keyboard_all_button_ru():
    kb = ask_walk_keyboard([], "ru")
    text = kb.inline_keyboard[0][0].text
    assert "Всем" in text


def test_ask_walk_keyboard_all_button_en():
    kb = ask_walk_keyboard([], "en")
    text = kb.inline_keyboard[0][0].text
    assert "Everyone" in text


def test_ask_walk_keyboard_single_user_with_display_name():
    user = make_user(display_name="Alice", telegram_id=111)
    kb = ask_walk_keyboard([user], "en")
    assert len(kb.inline_keyboard) == 2
    assert kb.inline_keyboard[1][0].text == "Alice"
    assert kb.inline_keyboard[1][0].callback_data == "ask_walk:111"


def test_ask_walk_keyboard_falls_back_to_username():
    user = make_user(username="alice_bot", telegram_id=222)
    kb = ask_walk_keyboard([user], "en")
    assert kb.inline_keyboard[1][0].text == "alice_bot"


def test_ask_walk_keyboard_falls_back_to_id():
    user = make_user(telegram_id=9999)
    kb = ask_walk_keyboard([user], "en")
    assert kb.inline_keyboard[1][0].text == "User 9999"


def test_ask_walk_keyboard_multiple_users():
    users = [
        make_user(display_name="Alice", telegram_id=1),
        make_user(display_name="Bob", telegram_id=2),
        make_user(display_name="Carol", telegram_id=3),
    ]
    kb = ask_walk_keyboard(users, "en")
    assert len(kb.inline_keyboard) == 4  # All + 3 users


def test_ask_walk_keyboard_user_order_preserved():
    users = [
        make_user(display_name="First", telegram_id=1),
        make_user(display_name="Second", telegram_id=2),
    ]
    kb = ask_walk_keyboard(users, "en")
    assert kb.inline_keyboard[1][0].text == "First"
    assert kb.inline_keyboard[2][0].text == "Second"


def test_ask_walk_keyboard_callback_contains_telegram_id():
    user = make_user(display_name="Alice", telegram_id=42)
    kb = ask_walk_keyboard([user], "en")
    assert "42" in kb.inline_keyboard[1][0].callback_data


def test_ask_walk_keyboard_display_name_beats_username():
    user = make_user(display_name="Display", username="username_fallback", telegram_id=1)
    kb = ask_walk_keyboard([user], "en")
    assert kb.inline_keyboard[1][0].text == "Display"


# ---------------------------------------------------------------------------
# main_keyboard contains ask_walk_button
# ---------------------------------------------------------------------------

def test_main_keyboard_has_ask_walk_button_ru():
    kb = main_keyboard("ru")
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert any("Попросить" in t for t in texts)


def test_main_keyboard_has_ask_walk_button_en():
    kb = main_keyboard("en")
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert any("Ask to walk" in t for t in texts)


# ---------------------------------------------------------------------------
# parameter_keyboard sanity
# ---------------------------------------------------------------------------

def test_parameter_keyboard_has_send_and_cancel_ru():
    kb = parameter_keyboard("ru")
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert any("Отправить" in t for t in texts)
    assert any("Отмена" in t for t in texts)


def test_parameter_keyboard_has_send_and_cancel_en():
    kb = parameter_keyboard("en")
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert any("Send" in t for t in texts)
    assert any("Cancel" in t for t in texts)
