import sqlite3
import json

db_path = "../../local_database/database.db"

def check():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, filename, is_analyzed, ai_summary FROM resumes ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    for row in rows:
        print(dict(row))
        
    conn.close()

if __name__ == "__main__":
    check()
