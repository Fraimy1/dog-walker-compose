from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.bot.config import settings

_SYNC_URL = settings.database_url.replace("+aiomysql", "+pymysql")
_ALEMBIC_INI = str(Path(__file__).resolve().parents[2] / "alembic.ini")

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def run_migrations() -> None:
    """Run pending alembic migrations.

    If the database already has tables but no alembic_version table (i.e. it
    was created by the old create_all approach) the DB is stamped at rev0001
    first so that only the delta migrations are applied.
    """
    alembic_cfg = Config(_ALEMBIC_INI)
    sync_engine = create_engine(_SYNC_URL)

    with sync_engine.connect() as conn:
        has_alembic = conn.execute(
            text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                 "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'alembic_version'")
        ).scalar_one_or_none()

        if not has_alembic:
            has_users = conn.execute(
                text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                     "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users'")
            ).scalar_one_or_none()

            if has_users:
                # Pre-alembic DB — stamp at initial revision so upgrade only
                # runs the deltas.
                command.stamp(alembic_cfg, "rev0001")

    command.upgrade(alembic_cfg, "head")
    sync_engine.dispose()
