from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
import os
import environ

# Set up Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'wallet_transaction_api.settings'
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(os.path.dirname(__file__), '../.env'))

from django.conf import settings
from sqlalchemy.ext.automap import automap_base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Создаем движок SQLAlchemy вручную
engine = create_engine(env('DATABASE_URL'))

# Автоматически отражаем существующие таблицы в метаданные SQLAlchemy
Base = automap_base()
Base.prepare(engine, reflect=True)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
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
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
