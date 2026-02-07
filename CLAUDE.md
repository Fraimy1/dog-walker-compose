# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot for logging dog walks with SQLite persistence. Users log walks via keyboard buttons, optionally add parameters (e.g., "Didn't poop", "Long walk") within a 5-minute window, and broadcast notifications to all active users. Supports bilingual operation (Russian/English) with per-user language preferences.

## Tech Stack

- **Python 3.10+** with **AIogram 3.x** (Telegram bot framework)
- **SQLAlchemy 2.0** with **aiosqlite** for async SQLite operations
- **Alembic** for database migrations
- **APScheduler 4.0** for timed walk auto-finalization
- **Loguru** for structured logging
- **Pydantic Settings** for configuration management

## Development Commands

```bash
# Install dependencies (requires uv or pip)
uv pip install -r requirements.txt
# or: pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your BOT_TOKEN

# Run the bot
python -m src.bot.main

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
# Note: Migrations run automatically on bot startup via run_migrations()

# Docker
docker build -t dog-walker-bot .
docker run -v $(pwd)/data:/app/data dog-walker-bot
```

## Architecture

### Module Responsibilities

- **src/bot/main.py**: Entry point, initializes bot, dispatcher, scheduler, and runs migrations
- **src/bot/handlers.py**: All message handlers and routing logic; maintains in-memory state for free-text input modes
- **src/bot/scheduler.py**: APScheduler integration for 5-minute walk auto-finalization timers
- **src/bot/keyboards.py**: Telegram ReplyKeyboardMarkup builders for UI
- **src/bot/i18n.py**: Bilingual text dictionary and localization helper
- **src/bot/config.py**: Pydantic Settings for environment-based config
- **src/database/models.py**: SQLAlchemy ORM models (User, Walk)
- **src/database/crud.py**: Database operations (get, create, update)
- **src/database/session.py**: Async engine, sessionmaker, and migration runner

### Key Flows

1. **Walk Logging (now)**:
   - User presses main button → creates pending Walk record → starts 5-minute timer → shows parameter keyboard
   - User toggles parameters or presses Send → finalizes Walk → broadcasts to all active users

2. **Walk Logging (past time)**:
   - User presses "log at time" button → enters free-text input mode (tracked in `_awaiting_time` set)
   - User types time (e.g., "14:30", "2 PM") → parses to closest past datetime → creates Walk with custom `walked_at`
   - Parser supports 12/24-hour formats; if no AM/PM, assumes closest past occurrence (may roll back to yesterday)

3. **Auto-finalization**:
   - When Walk is created, scheduler sets a 5-minute timer (APScheduler DateTrigger)
   - If user doesn't press Send, timer fires → `_auto_finalize_walk()` finalizes and broadcasts
   - Timer is cancelled if user manually sends or cancels walk

4. **Broadcast**:
   - After finalization, `_broadcast_walk()` sends notification to all active users
   - Notification includes walker's display name (or username), broadcast time, actual walk time, and any parameters
   - Each recipient sees the message in their own language

5. **User State Management**:
   - Module-level sets (`_awaiting_time`, `_awaiting_name`) track users in free-text input mode
   - Catch-all handler at end of router dispatches free-text input to appropriate state handler
   - State is cleared when user returns to normal button flow

### Database Schema

- **users**: `telegram_id` (unique), `username`, `display_name`, `language` (ru/en), `is_active`
- **walks**: `user_id` (FK), `walked_at`, `didnt_poop`, `long_walk`, `is_finalized`

### Migration Strategy

- Alembic manages schema changes
- `run_migrations()` auto-detects pre-Alembic databases (created via `create_all`) and stamps them at `rev0001` before applying deltas
- Always generate migrations for schema changes; do not use `create_all` in production

### Scheduler Lifecycle

- Global `_scheduler` and `_bot` are set in `init_scheduler(bot)` called from main
- Pending job IDs stored in `_pending_jobs` dict keyed by user_id for cancellation
- `schedule_walk_finalization()` cancels any existing timer for that user before scheduling new one
- Scheduler is properly cleaned up in `stop_scheduler()` on shutdown

## Configuration

Environment variables (loaded from `.env`):
- `BOT_TOKEN` (required): Telegram bot token
- `DATABASE_URL` (default: `sqlite+aiosqlite:///data/dog_walker.db`): Database connection string

## Logging

Loguru writes to both console (INFO+) and `data/bot.log` (DEBUG+) with rotation (10 MB, 7-day retention, gzip compression)
