TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "welcome": "Привет! Выберите язык:",
        "language_set": "Язык установлен. Теперь вы можете выгуливать собаку!",
        "walk_button": "🐕 Выгулять собаку",
        "didnt_poop": "💩 Не покакал",
        "long_walk": "🦮 Долгая прогулка",
        "send": "✅ Отправить",
        "walk_started": "Выберите параметры прогулки или нажмите «Отправить»:",
        "walk_logged": "🐕 {username} в {time}: выгулял собаку в {time_walked}",
        "additional": "Дополнительно: {params}",
        "param_didnt_poop": "не покакал",
        "param_long_walk": "долгая прогулка",
        "walk_sent": "Прогулка записана!",
        "no_active_walk": "Нет активной прогулки. Нажмите кнопку «Выгулять собаку».",
        "param_toggled": "Параметр обновлён.",
        "walk_at_time_button": "🕐 Прогулка в указанное время",
        "enter_time_prompt": (
            "Введите время прогулки.\n"
            "\n"
            "Поддерживаемые форматы:\n"
            "• 14:30, 23:00 (24-часовой)\n"
            "• 2 PM, 11:23 AM (12-часовой)\n"
            "• 2PM, 2:30PM\n"
            "\n"
            "Если AM/PM не указано, берётся ближайшее прошедшее время.\n"
            "Например, в 5:00 ввод «23» означает 23:00 вчера."
        ),
        "time_set": "Время установлено: {time}. Выберите параметры или нажмите «Отправить»:",
        "invalid_time": "Не удалось распознать время.\n\nПримеры: 14:30, 2 PM, 11:23AM",
        "yesterday": "вчера",
        "change_name_button": "✏️ Сменить имя",
        "change_name_prompt": "Текущее имя: {current}\n\nВведите новое имя:",
        "name_set": "Имя изменено на: {name}",
        "invalid_name": "Имя не может быть пустым.",
        "invalid_name_format": "Имя может содержать только буквы, цифры и пробелы (до 30 символов).",
        "cancel": "❌ Отмена",
        "walk_cancelled": "Прогулка отменена.",
        "stats_button": "📊 Статистика",
        "ask_walk_button": "🙏 Попросить выгулять",
        "ask_walk_choose": "Кому отправить запрос на прогулку?",
        "ask_walk_all": "👥 Всем",
        "ask_walk_request": "🐕 {requester} просит выгулять собаку!",
        "ask_walk_sent": "Запрос отправлен!",
        "ask_walk_no_users": "Нет других активных пользователей.",
    },
    "en": {
        "welcome": "Hello! Choose your language:",
        "language_set": "Language set. Now you can walk the dog!",
        "walk_button": "🐕 Walk the dog",
        "didnt_poop": "💩 Didn't poop",
        "long_walk": "🦮 Long walk",
        "send": "✅ Send",
        "walk_started": "Select walk parameters or press «Send»:",
        "walk_logged": "🐕 {username} at {time}: walked the dog at {time_walked}",
        "additional": "Additional: {params}",
        "param_didnt_poop": "didn't poop",
        "param_long_walk": "long walk",
        "walk_sent": "Walk logged!",
        "no_active_walk": "No active walk. Press «Walk the dog» button.",
        "param_toggled": "Parameter updated.",
        "walk_at_time_button": "🕐 Log walk at time",
        "enter_time_prompt": (
            "Enter the walk time.\n"
            "\n"
            "Supported formats:\n"
            "• 14:30, 23:00 (24-hour)\n"
            "• 2 PM, 11:23 AM (12-hour)\n"
            "• 2PM, 2:30PM\n"
            "\n"
            "If AM/PM is not specified, the closest past time is assumed.\n"
            "E.g. at 5:00 AM, entering «23» means 23:00 yesterday."
        ),
        "time_set": "Time set to: {time}. Select parameters or press «Send»:",
        "invalid_time": "Couldn't parse the time.\n\nExamples: 14:30, 2 PM, 11:23AM",
        "yesterday": "yesterday",
        "change_name_button": "✏️ Change name",
        "change_name_prompt": "Current name: {current}\n\nEnter your new name:",
        "name_set": "Name changed to: {name}",
        "invalid_name": "Name can't be empty.",
        "invalid_name_format": "Name can only contain letters, numbers and spaces (up to 30 characters).",
        "cancel": "❌ Cancel",
        "walk_cancelled": "Walk cancelled.",
        "stats_button": "📊 Statistics",
        "ask_walk_button": "🙏 Ask to walk",
        "ask_walk_choose": "Who should walk the dog?",
        "ask_walk_all": "👥 Everyone",
        "ask_walk_request": "🐕 {requester} wants someone to walk the dog!",
        "ask_walk_sent": "Request sent!",
        "ask_walk_no_users": "No other active users.",
    },
}


def get_text(key: str, lang: str = "ru") -> str:
    """Get localized text by key."""
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)
