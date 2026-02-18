# Dog Walker Bot

- [English](#english)
- [Russian / Русский](#русский)

---

## English

A private Telegram bot for a small group to log and track dog walks. When someone walks the dog, everyone in the group gets notified. Includes a web dashboard with walk statistics and charts.

### Features

- **One-tap walk logging** — press a button, optionally tag parameters, done
- **Custom walk times** — log a walk that happened earlier (e.g. "14:30", "2 PM")
- **Walk parameters** — mark walks as "didn't poop" or "long walk"
- **Auto-finalization** — walks auto-send after 5 minutes if you forget to press Send
- **Broadcast notifications** — all group members see who walked the dog and when
- **Bilingual** — Russian and English, per-user preference
- **Access control** — whitelist by Telegram user ID, only your people get in
- **Custom display names** — each user can set how their name appears in broadcasts
- **Web dashboard** — charts and stats at `localhost:8000`, filterable by date and walker

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌───────────────┐  │
│  │   bot    │    │   web    │    │     mysql     │  │
│  │          │    │          │    │               │  │
│  │ AIogram  │    │ FastAPI  │    │  MySQL 8.0    │  │
│  │ Telegram │    │ Uvicorn  │    │  persistent   │  │
│  │ polling  │    │ :8000    │    │  volume       │  │
│  └────┬─────┘    └────┬─────┘    └──────┬────────┘  │
│       │               │                 │            │
│       └───────────────┴─────────────────┘            │
│                   backend network                    │
│                                                      │
│  ┌──────────┐  (dev profile only)                    │
│  │ adminer  │─────────────────────────────────────── │
│  │  :8080   │  MySQL web UI                          │
│  └──────────┘                                        │
└─────────────────────────────────────────────────────┘
```

**Services:**
- `bot` — Telegram bot (AIogram 3, long polling)
- `web` — FastAPI dashboard served on port 8000 (multi-stage Docker build)
- `mysql` — MySQL 8.0 database with healthcheck and named volume for persistence
- `adminer` — MySQL web UI on port 8080, available under the `dev` profile only

### Quick Start

#### 1. Clone and configure

```bash
git clone https://github.com/Fraimy1/dog-walker-compose.git
cd dog-walker-compose
cp .env.example .env
```

Edit `.env` with your values (see [Configuration](#configuration) below).

#### 2. Start

```bash
docker compose up -d
```

Dashboard is available at `http://localhost:8000`.

#### 3. Start with dev tools (Adminer DB UI at port 8080)

```bash
docker compose --profile dev up -d
```

#### 4. Stop

```bash
docker compose down
```

To also delete the database volume:

```bash
docker compose down -v
```

### Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | No | Comma-separated Telegram user IDs to whitelist (empty = allow all) |
| `MYSQL_USER` | Yes | MySQL username |
| `MYSQL_PASSWORD` | Yes | MySQL password |
| `MYSQL_ROOT_PASSWORD` | Yes | MySQL root password |
| `MYSQL_DATABASE` | Yes | MySQL database name |
| `DATABASE_URL` | Yes | Full connection string — must match the MySQL credentials above |

**Example `.env`:**
```env
BOT_TOKEN=1234567890:ABCdef...
ALLOWED_USERS=111111111,222222222
MYSQL_USER=dogwalker
MYSQL_PASSWORD=secret123
MYSQL_ROOT_PASSWORD=rootsecret123
MYSQL_DATABASE=dogwalker
DATABASE_URL=mysql+aiomysql://dogwalker:secret123@mysql:3306/dogwalker
```

#### Getting Telegram user IDs

Message [@userinfobot](https://t.me/userinfobot) on Telegram — it replies with your numeric ID.

### How It Works

1. `/start` — choose language (Russian or English)
2. Press **Walk the dog** — starts a new walk with a 5-minute timer
3. Optionally toggle **Didn't poop** / **Long walk**
4. Press **Send** (or wait for auto-send) — walk is logged and broadcast to all users
5. To log a past walk, press **Log walk at time** and type the time (e.g. `14:30`, `2 PM`)

### Tech Stack

| Component | Technology |
|---|---|
| Bot framework | Python 3.12 / AIogram 3.x |
| Web framework | FastAPI + Uvicorn |
| Database | MySQL 8.0 (via SQLAlchemy 2.0 async + aiomysql) |
| Migrations | Alembic |
| Scheduling | APScheduler 4.0 |
| Logging | Loguru |
| Config | Pydantic Settings |
| Containerization | Docker + Docker Compose |

---

## Русский

Приватный Telegram-бот для небольшой группы, позволяющий отмечать и отслеживать прогулки с собакой. Когда кто-то выгуливает собаку, все участники получают уведомление. Включает веб-дашборд со статистикой.

### Возможности

- **Запись прогулки в одно нажатие** — нажмите кнопку, при желании отметьте параметры, готово
- **Произвольное время** — запишите прогулку, которая была раньше (например, "14:30", "2 PM")
- **Параметры прогулки** — отметьте «не покакал» или «долгая прогулка»
- **Автоматическая отправка** — прогулка отправляется автоматически через 5 минут
- **Уведомления** — все участники группы видят, кто выгулял собаку и когда
- **Двуязычный интерфейс** — русский и английский, настраивается для каждого пользователя
- **Контроль доступа** — белый список по Telegram ID
- **Пользовательские имена** — каждый может задать отображаемое имя
- **Веб-дашборд** — графики и статистика на `localhost:8000`

### Архитектура

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌───────────────┐  │
│  │   bot    │    │   web    │    │     mysql     │  │
│  │          │    │          │    │               │  │
│  │ AIogram  │    │ FastAPI  │    │  MySQL 8.0    │  │
│  │ Telegram │    │ Uvicorn  │    │  том для      │  │
│  │ polling  │    │ :8000    │    │  хранения     │  │
│  └────┬─────┘    └────┬─────┘    └──────┬────────┘  │
│       │               │                 │            │
│       └───────────────┴─────────────────┘            │
│                  сеть backend                        │
│                                                      │
│  ┌──────────┐  (только профиль dev)                  │
│  │ adminer  │                                        │
│  │  :8080   │  Веб-интерфейс для MySQL               │
│  └──────────┘                                        │
└─────────────────────────────────────────────────────┘
```

**Сервисы:**
- `bot` — Telegram-бот (AIogram 3, long polling)
- `web` — FastAPI дашборд на порту 8000 (multi-stage Docker сборка)
- `mysql` — MySQL 8.0 с healthcheck и именованным томом для persistence
- `adminer` — веб-интерфейс для MySQL на порту 8080, только в профиле `dev`

### Быстрый старт

#### 1. Клонировать и настроить

```bash
git clone https://github.com/Fraimy1/dog-walker-compose.git
cd dog-walker-compose
cp .env.example .env
```

Отредактируйте `.env` (см. раздел [Конфигурация](#конфигурация)).

#### 2. Запустить

```bash
docker compose up -d
```

Дашборд доступен на `http://localhost:8000`.

#### 3. Запуск с инструментами разработки (Adminer на порту 8080)

```bash
docker compose --profile dev up -d
```

#### 4. Остановить

```bash
docker compose down
```

Остановить и удалить базу данных:

```bash
docker compose down -v
```

### Конфигурация

Скопируйте `.env.example` в `.env` и заполните значения:

| Переменная | Обязательна | Описание |
|---|---|---|
| `BOT_TOKEN` | Да | Токен бота от [@BotFather](https://t.me/BotFather) |
| `ALLOWED_USERS` | Нет | Telegram ID через запятую (пусто = все допущены) |
| `MYSQL_USER` | Да | Пользователь MySQL |
| `MYSQL_PASSWORD` | Да | Пароль MySQL |
| `MYSQL_ROOT_PASSWORD` | Да | Root-пароль MySQL |
| `MYSQL_DATABASE` | Да | Имя базы данных |
| `DATABASE_URL` | Да | Строка подключения (должна совпадать с MySQL-данными выше) |

**Пример `.env`:**
```env
BOT_TOKEN=1234567890:ABCdef...
ALLOWED_USERS=111111111,222222222
MYSQL_USER=dogwalker
MYSQL_PASSWORD=secret123
MYSQL_ROOT_PASSWORD=rootsecret123
MYSQL_DATABASE=dogwalker
DATABASE_URL=mysql+aiomysql://dogwalker:secret123@mysql:3306/dogwalker
```

#### Как узнать Telegram ID

Напишите [@userinfobot](https://t.me/userinfobot) — бот ответит вашим числовым ID.

### Как это работает

1. `/start` — выберите язык
2. Нажмите **Выгулять собаку** — начинается прогулка с 5-минутным таймером
3. При желании отметьте **Не покакал** / **Долгая прогулка**
4. Нажмите **Отправить** (или подождите автоотправку) — прогулка записана
5. Для прошедшей прогулки — **Прогулка в указанное время**, введите время

### Технологии

| Компонент | Технология |
|---|---|
| Бот | Python 3.12 / AIogram 3.x |
| Веб | FastAPI + Uvicorn |
| База данных | MySQL 8.0 (SQLAlchemy 2.0 async + aiomysql) |
| Миграции | Alembic |
| Планировщик | APScheduler 4.0 |
| Логирование | Loguru |
| Конфигурация | Pydantic Settings |
| Контейнеризация | Docker + Docker Compose |
