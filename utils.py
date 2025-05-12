import sqlite3

def load_training_data(path="training_data.txt") -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def connect_db(path="chinook.db"):
    return sqlite3.connect(path)

def run_query(cursor, sql: str):
    try:
        cleaned_sql = sql.strip().rstrip(';')  # Remove trailing semicolon
        cursor.execute(cleaned_sql)
        return cursor.fetchall()
    except Exception as e:
        return f"SQL Error: {e}"

