from sqlalchemy import create_engine
from alembic import context

from src.bot.config import settings
from src.database.models import Base

# Alembic runs synchronously — strip the async driver from the URL
_SYNC_URL = settings.database_url.replace("+aiosqlite", "")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=_SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_SYNC_URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
