"""
alembic/env.py
--------------
Alembic migration environment configuration.

This file tells Alembic:
  1. How to connect to the database (uses settings.database_url from .env)
  2. Which models to inspect for schema changes (imports Base from database.py)
  3. How to run migrations (online = connected, offline = generates SQL script)

KEY LINE: target_metadata = Base.metadata
  This tells Alembic to compare the current DB schema against ALL
  SQLAlchemy models that inherit from Base (UserModel, TaskModel).
  When you run 'alembic revision --autogenerate', it detects differences
  and writes migration code automatically.
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import settings to get DATABASE_URL from .env
from config import settings

# Import Base AND all models so Alembic sees the table definitions
from database import Base
from models.db_models import UserModel, TaskModel  # noqa: F401 — must import to register

# Alembic Config object (reads alembic.ini)
config = context.config

# Override the sqlalchemy.url in alembic.ini with the value from .env
# This means you only need to set DATABASE_URL in one place
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what makes --autogenerate work
# Alembic compares Base.metadata (your models) with the actual DB schema
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates a .sql file instead of running against the DB.
    Useful when you don't have direct DB access.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the actual database and applies migrations.
    This is what 'alembic upgrade head' uses.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,   # No pooling for migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# Decide which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
