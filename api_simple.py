import sqlite3
import secrets
import datetime

# Автоматически создаём таблицы при запуске
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            api_key TEXT UNIQUE,
            balance REAL DEFAULT 0.0,
            created_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            query_text TEXT,
            search_type TEXT,
            cost REAL DEFAULT 0.25,
            timestamp TIMESTAMP,
            status TEXT,
            FOREIGN KEY (partner_id) REFERENCES partners(id)
        )
    ''')
    
    # Добавляем тестового партнёра, если нет ни одного
    cursor.execute('SELECT COUNT(*) FROM partners')
    count = cursor.fetchone()[0]
    if count == 0:
        api_key = secrets.token_hex(16)
        cursor.execute('''
            INSERT INTO partners (name, api_key, balance, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('Первый партнёр', api_key, 10.0, datetime.datetime.now()))
        print(f"✅ Создан тестовый партнёр с ключом: {api_key}")
    
    conn.commit()
    conn.close()

# Вызываем при запуске
init_db()
