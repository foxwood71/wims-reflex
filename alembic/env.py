# wims/alembic/env.py

import sys
import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
# [추가] Reflex를 인식하도록 추가
import reflex as rx

from alembic import context

# [추가] project root를 인식하도록 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# [편집] autogenerate가 모든 모델을 인식하도록 설정
from wims import models     # noqa: F401, E402
# target_metadata = mymodel.Base.metadata
# target_metadata = None
# [편집] SQLModel을 인식하도록 설정
target_metadata = rx.Model.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # [추가] autogenerate가 모든 스키마를 인식하도록 설정
        include_schemas=True,
        # [추가] 타입 및 서버 기본값 비교를 활성화하여 더 정확하게 감지합니다.
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # [추가] autogenerate가 모든 스키마를 인식하도록 설정
            include_schemas=True,
            # [추가] 타입 및 서버 기본값 비교를 활성화하여 더 정확하게 감지합니다.
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
