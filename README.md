# Dog Walker Bot

- [English](#english)
- [Russian / Русский](#русский)

---

## English

A private Telegram bot for a small group to log and track dog walks. When someone walks the dog, everyone in the group gets notified.

### Features

- **One-tap walk logging** -- press a button, optionally tag parameters, done
- **Custom walk times** -- log a walk that happened earlier (e.g. "14:30", "2 PM")
- **Walk parameters** -- mark walks as "didn't poop" or "long walk"
- **Auto-finalization** -- walks auto-send after 5 minutes if you forget to press Send
- **Broadcast notifications** -- all group members see who walked the dog and when
- **Bilingual** -- Russian and English, per-user preference
- **Access control** -- whitelist by Telegram user ID, only your people get in
- **Custom display names** -- each user can set how their name appears in broadcasts

### Quick Start

#### Docker (recommended)

```bash
docker build -t dog-walker-bot .
docker run -d \
  -e BOT_TOKEN=your_token_here \
  -e ALLOWED_USERS='[111111111,222222222]' \
  -v dog-walker-data:/app/data \
  dog-walker-bot
```

#### Docker Compose

```yaml
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=your_token_here
      - ALLOWED_USERS=[111111111,222222222]
    volumes:
      - bot-data:/app/data
    restart: unless-stopped

volumes:
  bot-data:
```

#### Manual

```bash
# Clone and install
git clone https://github.com/Fraimy1/dog-walker.git
cd dog-walker
uv sync

# Configure
cp .env.example .env
# Edit .env with your values

# Run
python -m src.bot.main
```

### Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | -- | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | No | `[]` (allow all) | JSON list of Telegram user IDs to whitelist |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///data/dog_walker.db` | Database connection string |

#### Getting Telegram user IDs

Message [@userinfobot](https://t.me/userinfobot) on Telegram -- it replies with your numeric ID. Collect IDs from everyone who should have access and add them to `ALLOWED_USERS`.

### How It Works

1. `/start` -- choose language (Russian or English)
2. Press **Walk the dog** -- starts a new walk with a 5-minute timer
3. Optionally toggle **Didn't poop** / **Long walk**
4. Press **Send** (or wait for auto-send) -- walk is logged and broadcast to all users
5. To log a past walk, press **Log walk at time** and type the time (e.g. `14:30`, `2 PM`)

### Data

All data is stored in a SQLite database at `data/dog_walker.db`. Mount `/app/data` as a volume in Docker to persist across container restarts. Logs are written to `data/bot.log` with 10 MB rotation and 7-day retention.

### Tech Stack

Python 3.10+ / AIogram 3 / SQLAlchemy 2 / Alembic / APScheduler 4 / Loguru

---

## Русский

Приватный Telegram-бот для небольшой группы, позволяющий отмечать и отслеживать прогулки с собакой. Когда кто-то выгуливает собаку, все участники получают уведомление.

### Возможности

- **Запись прогулки в одно нажатие** -- нажмите кнопку, при желании отметьте параметры, готово
- **Произвольное время** -- запишите прогулку, которая была раньше (например, "14:30", "2 PM")
- **Параметры прогулки** -- отметьте «не покакал» или «долгая прогулка»
- **Автоматическая отправка** -- прогулка отправляется автоматически через 5 минут, если вы забыли нажать «Отправить»
- **Уведомления** -- все участники группы видят, кто выгулял собаку и когда
- **Двуязычный интерфейс** -- русский и английский, настраивается для каждого пользователя
- **Контроль доступа** -- белый список по Telegram ID, доступ только для своих
- **Пользовательские имена** -- каждый может задать, как его имя отображается в уведомлениях

### Быстрый старт

#### Docker (рекомендуется)

```bash
docker build -t dog-walker-bot .
docker run -d \
  -e BOT_TOKEN=ваш_токен \
  -e ALLOWED_USERS='[111111111,222222222]' \
  -v dog-walker-data:/app/data \
  dog-walker-bot
```

#### Docker Compose

```yaml
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=ваш_токен
      - ALLOWED_USERS=[111111111,222222222]
    volumes:
      - bot-data:/app/data
    restart: unless-stopped

volumes:
  bot-data:
```

#### Вручную

```bash
# Клонировать и установить
git clone https://github.com/Fraimy1/dog-walker.git
cd dog-walker
uv sync

# Настроить
cp .env.example .env
# Отредактируйте .env и укажите свои значения

# Запустить
python -m src.bot.main
```

### Конфигурация

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `BOT_TOKEN` | Да | -- | Токен Telegram-бота от [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | Нет | `[]` (все допущены) | JSON-список Telegram ID пользователей для белого списка |
| `DATABASE_URL` | Нет | `sqlite+aiosqlite:///data/dog_walker.db` | Строка подключения к базе данных |

#### Как узнать Telegram ID

Напишите [@userinfobot](https://t.me/userinfobot) в Telegram -- бот ответит вашим числовым ID. Соберите ID всех, кому нужен доступ, и добавьте их в `ALLOWED_USERS`.

### Как это работает

1. `/start` -- выберите язык (русский или английский)
2. Нажмите **Выгулять собаку** -- начинается новая прогулка с 5-минутным таймером
3. При желании отметьте **Не покакал** / **Долгая прогулка**
4. Нажмите **Отправить** (или подождите автоотправку) -- прогулка записана, уведомление отправлено всем
5. Чтобы записать прошедшую прогулку, нажмите **Прогулка в указанное время** и введите время (например, `14:30`, `2 PM`)

### Данные

Все данные хранятся в базе SQLite по пути `data/dog_walker.db`. Смонтируйте `/app/data` как том в Docker для сохранения данных между перезапусками. Логи пишутся в `data/bot.log` с ротацией 10 МБ и хранением 7 дней.

### Технологии

Python 3.10+ / AIogram 3 / SQLAlchemy 2 / Alembic / APScheduler 4 / Loguru
