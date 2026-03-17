from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import os

app = FastAPI()

class SearchRequest(BaseModel):
    api_key: str
    type: str
    query: str

def get_db():
    return sqlite3.connect('bot_database.db')

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
    
    # Здесь заглушка вместо поиска
    results = [{"First Name": "John", "Last Name": "Smith", "Age": 35}]
    
    cursor.execute('''
        UPDATE partners SET balance = balance - 0.25 
        WHERE id = ?
    ''', (partner_id,))
    
    db.commit()
    db.close()
    
    return {"success": True, "data": results}

@app.get("/")
def root():
    return {"message": "API работает"}