#!/usr/bin/env python
import sqlite3
import os

db_path = 'estateiq.db'

if not os.path.exists(db_path):
    print(f"Database file does not exist: {db_path}")
else:
    print(f"Database file size: {os.path.getsize(db_path)} bytes")
    
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\nTables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
        # Get row count for each table
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
    
    conn.close()
    print("\nDatabase connection successful!")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
