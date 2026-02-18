# Dog Walker Bot

- [English](#english)
- [Russian / Русский](#русский)

---

## English

A private Telegram bot for a small group to log and track dog walks. When someone walks the dog, everyone gets notified.

### Quick Start

```bash
docker run -d \
  -e BOT_TOKEN=your_token_here \
  -e ALLOWED_USERS='[111111111,222222222]' \
  -v dog-walker-data:/app/data \
  blaze698/dog-walker-bot
```

Or use `--env-file` to keep secrets out of your shell history:

```bash
docker run -d --env-file .env -v dog-walker-data:/app/data blaze698/dog-walker-bot
```

### Docker Compose

```yaml
services:
  bot:
    image: blaze698/dog-walker-bot
    environment:
      - BOT_TOKEN=your_token_here
      - ALLOWED_USERS=[111111111,222222222]
    volumes:
      - bot-data:/app/data
    restart: unless-stopped

volumes:
  bot-data:
```

### Environment Variables

| Variable        | Required | Default                                  | Description                                                  |
| --------------- | -------- | ---------------------------------------- | ------------------------------------------------------------ |
| `BOT_TOKEN`     | Yes      | --                                       | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | No       | `[]` (allow all)                         | JSON list of Telegram user IDs to whitelist                  |
| `DATABASE_URL`  | No       | `sqlite+aiosqlite:///data/dog_walker.db` | Database connection string                                   |

### Data Persistence

Mount `/app/data` as a volume to persist the SQLite database and logs across container restarts.

### Getting Telegram User IDs

Message [@userinfobot](https://t.me/userinfobot) on Telegram to get your numeric user ID. Add all authorized user IDs to `ALLOWED_USERS`.

### Features

- One-tap walk logging with optional parameters (didn't poop, long walk)
- Log past walks by typing a time (e.g. "14:30", "2 PM")
- Auto-finalization after 5 minutes
- Broadcast notifications to all group members
- Bilingual: Russian and English
- Whitelist access control by Telegram user ID

### Source Code

[GitHub](https://github.com/Fraimy1/dog-walker)

---

## Русский

Приватный Telegram-бот для небольшой группы, позволяющий отмечать и отслеживать прогулки с собакой. Когда кто-то выгуливает собаку, все участники получают уведомление.

### Быстрый старт

```bash
docker run -d \
  -e BOT_TOKEN=ваш_токен \
  -e ALLOWED_USERS='[111111111,222222222]' \
  -v dog-walker-data:/app/data \
  blaze698/dog-walker-bot
```

Или используйте `--env-file`, чтобы не светить секреты в истории команд:

```bash
docker run -d --env-file .env -v dog-walker-data:/app/data blaze698/dog-walker-bot
```

### Docker Compose

```yaml
services:
  bot:
    image: blaze698/dog-walker-bot
    environment:
      - BOT_TOKEN=ваш_токен
      - ALLOWED_USERS=[111111111,222222222]
    volumes:
      - bot-data:/app/data
    restart: unless-stopped

volumes:
  bot-data:
```

### Переменные окружения

| Переменная      | Обязательна | По умолчанию                             | Описание                                                    |
| --------------- | ----------- | ---------------------------------------- | ----------------------------------------------------------- |
| `BOT_TOKEN`     | Да          | --                                       | Токен Telegram-бота от [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | Нет         | `[]` (все допущены)                      | JSON-список Telegram ID пользователей для белого списка     |
| `DATABASE_URL`  | Нет         | `sqlite+aiosqlite:///data/dog_walker.db` | Строка подключения к базе данных                            |

### Хранение данных

Смонтируйте `/app/data` как том, чтобы сохранить базу данных SQLite и логи между перезапусками контейнера.

### Как узнать Telegram ID

Напишите [@userinfobot](https://t.me/userinfobot) в Telegram -- бот ответит вашим числовым ID. Добавьте ID всех авторизованных пользователей в `ALLOWED_USERS`.

### Возможности

- Запись прогулки в одно нажатие с опциональными параметрами (не покакал, долгая прогулка)
- Запись прогулок за прошедшее время (например, "14:30", "2 PM")
- Автоматическая отправка через 5 минут
- Уведомления всем участникам группы
- Двуязычный интерфейс: русский и английский
- Контроль доступа по белому списку Telegram ID

### Исходный код

[GitHub](https://github.com/Fraimy1/dog-walker)
