import sqlite3
import secrets
import datetime

# Подключаемся к твоей базе
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Создаём таблицу партнёров
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

# Создаём таблицу для логов запросов
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

# Добавляем первого партнёра
api_key = secrets.token_hex(16)  # генерирует случайный ключ
cursor.execute('''
    INSERT INTO partners (name, api_key, balance, created_at)
    VALUES (?, ?, ?, ?)
''', ('Первый партнёр', api_key, 10.0, datetime.datetime.now()))

conn.commit()
conn.close()

print("=" * 50)
print("✅ Таблицы для партнёров созданы!")
print("=" * 50)
print(f"🔑 API ключ для первого партнёра:")
print(f"{api_key}")
print("=" * 50)
print("Сохрани этот ключ, он понадобится для теста")
print("=" * 50)