import sqlite3

def setup_database():
    conn = sqlite3.connect('employees.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    conn.close()

if __name__ == '__main__':
    setup_database()
