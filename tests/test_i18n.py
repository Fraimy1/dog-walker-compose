"""Tests for the i18n module."""
import pytest

from src.bot.i18n import TEXTS, get_text

LANGUAGES = ("ru", "en")

REQUIRED_KEYS = [
    "welcome",
    "language_set",
    "walk_button",
    "didnt_poop",
    "long_walk",
    "send",
    "walk_started",
    "walk_logged",
    "additional",
    "param_didnt_poop",
    "param_long_walk",
    "walk_sent",
    "no_active_walk",
    "param_toggled",
    "walk_at_time_button",
    "enter_time_prompt",
    "time_set",
    "invalid_time",
    "yesterday",
    "change_name_button",
    "change_name_prompt",
    "name_set",
    "invalid_name",
    "invalid_name_format",
    "cancel",
    "walk_cancelled",
    "stats_button",
    # ask-to-walk keys
    "ask_walk_button",
    "ask_walk_choose",
    "ask_walk_all",
    "ask_walk_request",
    "ask_walk_sent",
    "ask_walk_no_users",
]


# ---------------------------------------------------------------------------
# Structure integrity
# ---------------------------------------------------------------------------

def test_both_languages_present():
    assert "ru" in TEXTS
    assert "en" in TEXTS


@pytest.mark.parametrize("key", REQUIRED_KEYS)
def test_key_exists_in_ru(key):
    assert key in TEXTS["ru"], f"Key {key!r} missing from Russian texts"


@pytest.mark.parametrize("key", REQUIRED_KEYS)
def test_key_exists_in_en(key):
    assert key in TEXTS["en"], f"Key {key!r} missing from English texts"


def test_ru_and_en_have_same_keys():
    assert set(TEXTS["ru"].keys()) == set(TEXTS["en"].keys())


# ---------------------------------------------------------------------------
# get_text behaviour
# ---------------------------------------------------------------------------

def test_get_text_returns_ru_by_default():
    result = get_text("walk_button")
    assert result == TEXTS["ru"]["walk_button"]


def test_get_text_returns_en():
    result = get_text("walk_button", "en")
    assert result == TEXTS["en"]["walk_button"]


def test_get_text_fallback_unknown_lang():
    result = get_text("walk_button", "fr")
    assert result == TEXTS["ru"]["walk_button"]


def test_get_text_missing_key_returns_key():
    result = get_text("this_key_does_not_exist", "en")
    assert result == "this_key_does_not_exist"


def test_get_text_all_values_are_strings():
    for lang in LANGUAGES:
        for key, value in TEXTS[lang].items():
            assert isinstance(value, str), f"TEXTS[{lang!r}][{key!r}] is not a string"


def test_get_text_no_empty_values():
    for lang in LANGUAGES:
        for key, value in TEXTS[lang].items():
            assert value.strip(), f"TEXTS[{lang!r}][{key!r}] is empty"


# ---------------------------------------------------------------------------
# ask_walk keys are non-empty and bilingual
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lang", LANGUAGES)
def test_ask_walk_request_has_placeholder(lang):
    assert "{requester}" in TEXTS[lang]["ask_walk_request"]


@pytest.mark.parametrize("lang", LANGUAGES)
def test_ask_walk_button_not_empty(lang):
    assert len(TEXTS[lang]["ask_walk_button"]) > 0


@pytest.mark.parametrize("lang", LANGUAGES)
def test_ask_walk_all_not_empty(lang):
    assert len(TEXTS[lang]["ask_walk_all"]) > 0
