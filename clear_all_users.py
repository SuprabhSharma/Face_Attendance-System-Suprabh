from app.models.db import get_db_connection

def clear_all_users_except_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all non-admin user IDs
        cursor.execute("SELECT id FROM users WHERE role != 'admin'")
        user_ids = [row[0] for row in cursor.fetchall()]

        if not user_ids:
            print("ℹ️ No non-admin users found")
            return

        # Delete attendance for non-admin users
        cursor.executemany(
            "DELETE FROM attendance WHERE user_id = ?", 
            [(uid,) for uid in user_ids]
        )

        # Delete email logs
        cursor.executemany(
            "DELETE FROM email_notifications WHERE user_id = ?", 
            [(uid,) for uid in user_ids]
        )

        # Delete users (this also removes face embeddings)
        cursor.execute("DELETE FROM users WHERE role != 'admin'")

        conn.commit()
        print("✅ All users (except admin) and their face data deleted successfully")

    except Exception as e:
        print("❌ Error:", str(e))

    finally:
        conn.close()


if __name__ == "__main__":
    confirm = input("⚠️ This will DELETE ALL USERS except ADMIN. Type 'YES' to continue: ")

    if confirm.strip().lower() == "yes":
        clear_all_users_except_admin()
    else:
        print("❌ Operation cancelled")