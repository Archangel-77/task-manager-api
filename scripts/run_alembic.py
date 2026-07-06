from alembic.config import Config
from alembic import command

config = Config("alembic.ini")
command.upgrade(config, "head")