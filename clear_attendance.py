from app.models.db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM attendance")

conn.commit()
conn.close()

print("All attendance deleted successfully")