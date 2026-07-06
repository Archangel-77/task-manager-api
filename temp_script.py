import sqlite3

connection = sqlite3.connect('.coverage')
cursor = connection.cursor()

# Query to get column information for the 'users' table
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()
print("\nColumns in 'users':")
for column in columns:
    print(column)

connection.close()