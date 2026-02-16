import sqlite3
import os

db_path = os.path.join("local_database", "database.db")

if not os.path.exists(db_path):
    print(f"DATABASE NOT FOUND at {db_path}")
else:
    print(f"Database found at {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        
        # Check users
        if ('users',) in tables:
            cursor.execute("SELECT id, username, email FROM users")
            users = cursor.fetchall()
            print(f"Users found ({len(users)}):")
            for u in users:
                print(u)
        else:
            print("Users table does not exist!")
            
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
