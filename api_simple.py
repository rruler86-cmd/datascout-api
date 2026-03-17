from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import secrets
import os

app = FastAPI()

# Модель запроса
class SearchRequest(BaseModel):
    api_key: str
    type: str
    query: str

# Инициализация базы данных
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
    
    cursor.execute('SELECT COUNT(*) FROM partners')
    if cursor.fetchone()[0] == 0:
        api_key = secrets.token_hex(16)
        cursor.execute('''
            INSERT INTO partners (name, api_key, balance, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('Тестовый партнёр', api_key, 10.0, datetime.datetime.now()))
        print(f"✅ Создан тестовый партнёр с ключом: {api_key}")
    
    conn.commit()
    conn.close()

# Запускаем инициализацию
init_db()

# Подключение к БД
def get_db():
    return sqlite3.connect('bot_database.db')

# ВРЕМЕННАЯ ЗАГЛУШКА
def fake_search(search_type, query):
    return [{"First Name": "John", "Last Name": "Smith", "Age": 35}]

@app.post("/search")
def search_partner(request: SearchRequest):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, balance FROM partners 
        WHERE api_key = ? AND is_active = 1
    ''', (request.api_key,))
    partner = cursor.fetchone()
    
    if not partner:
        raise HTTPException(401, "Неверный API ключ")
    
    partner_id, balance = partner
    
    if balance < 0.25:
        raise HTTPException(402, "Недостаточно средств")
    
    results = fake_search(request.type, request.query)
    
    cursor.execute('''
        UPDATE partners SET balance = balance - 0.25 
        WHERE id = ?
    ''', (partner_id,))
    
    cursor.execute('''
        INSERT INTO partner_queries 
        (partner_id, query_text, search_type, cost, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (partner_id, request.query, request.type, 0.25, datetime.datetime.now(), 'success'))
    
    db.commit()
    db.close()
    
    return {"success": True, "data": results}

@app.get("/")
def root():
    return {"message": "API работает"}

@app.get("/balance/{api_key}")
def get_balance(api_key: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT balance FROM partners WHERE api_key = ?', (api_key,))
    row = cursor.fetchone()
    db.close()
    
    if not row:
        raise HTTPException(404, "Партнёр не найден")
    
    return {"balance": row[0]}
