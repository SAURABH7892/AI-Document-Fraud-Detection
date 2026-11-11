import sqlite3

conn = sqlite3.connect('docshield.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE verification_results ADD COLUMN issuer_metadata JSON DEFAULT '{}'")
    conn.commit()
    print("Column issuer_metadata added successfully.")
except Exception as e:
    print("Migration info:", e)
conn.close()
