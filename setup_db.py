# ============================================
# setup_db.py - Run this ONCE to initialise
#               the MySQL database & sample data
# ============================================

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def run_setup():
    # First connect WITHOUT selecting a database
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )
    cursor = conn.cursor()

    # Read and split the SQL file
    with open("database.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    # Execute each statement individually
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        try:
            cursor.execute(stmt)
            conn.commit()
        except Error as e:
            # Ignore duplicate-entry errors (safe re-run)
            if "Duplicate entry" in str(e) or "already exists" in str(e).lower():
                pass
            else:
                print(f"  [WARN] {e}")

    cursor.close()
    conn.close()
    print("✅ Database setup complete!")
    print("   Default login → username: admin  |  password: admin123")

if __name__ == "__main__":
    run_setup()
