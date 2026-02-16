import sqlite3
import os

db_path = os.path.join("apps", "backend", "data", "database.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for user with trailing space
    cursor.execute("SELECT id, username FROM users WHERE username LIKE '% '")
    users = cursor.fetchall()
    
    if users:
        print(f"Found {len(users)} users with trailing spaces:")
        for u in users:
            old_username = u[1]
            new_username = old_username.strip()
            print(f"Fixing User ID {u[0]}: '{old_username}' -> '{new_username}'")
            
            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, u[0]))
        
        conn.commit()
        print("Database updated successfully.")
    else:
        print("No users with trailing spaces found.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
