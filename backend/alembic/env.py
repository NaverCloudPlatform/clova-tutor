# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

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
# target_metadata = mymodel.Base.metadata

# 같은 Base를 공유한다는 사실을 alembic에게 알리기 위해 명시적으로 import 해야됩니다.
from common.database.base import Base
import all_models

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
from config.config import db_config as app_config

config.set_main_option(
    "sqlalchemy.url",
    "mysql+pymysql://"
    + app_config.MYSQL_USER
    + ":"
    + app_config.MYSQL_PASSWORD
    + "@"
    + app_config.MYSQL_HOST
    + ":"
    + app_config.MYSQL_PORT
    + "/"
    + app_config.MYSQL_DB,
)

from sqlalchemy.schema import ForeignKeyConstraint


# foreign key 정보를 제거 (실제 DB에 fk 정보를 생성하지 않기 위함)
def remove_foreign_keys(metadata):
    for table in metadata.tables.values():
        fk_constraints = [
            c for c in table.constraints if isinstance(c, ForeignKeyConstraint)
        ]
        for fk in fk_constraints:
            table.constraints.remove(fk)


remove_foreign_keys(target_metadata)


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
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
