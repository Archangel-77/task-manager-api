import sqlite3

def check_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a list of table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        print(table[0])
    
    conn.close()

if __name__ == "__main__":
    db_path = "alembic/alembic.db"
    check_tables(db_path)