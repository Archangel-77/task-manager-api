import sqlite3
from sqlalchemy import create_engine

def create_database(db_path):
    engine = create_engine(f"sqlite:///{db_path}")
    connection = engine.connect()
    connection.close()

if __name__ == "__main__":
    db_path = "alembic/alembic.db"
    create_database(db_path)