import sqlite3

def verify_database():
    """Verify the database contents"""
    conn = sqlite3.connect('khpet27_data.db')
    cursor = conn.cursor()
    
    # Check total count
    cursor.execute("SELECT COUNT(*) FROM objects")
    total_count = cursor.fetchone()[0]
    print(f"Всего записей в базе данных: {total_count}")
    
    # Show sample records
    cursor.execute("SELECT id, name, audio, image, text FROM objects ORDER BY id LIMIT 5")
    records = cursor.fetchall()
    
    print("\nПримеры записей:")
    print("-" * 80)
    for record in records:
        print(f"ID: {record[0]}")
        print(f"Name: {record[1]}")
        print(f"Audio: {record[2]}")
        print(f"Image: {record[3]}")
        print(f"Text: {record[4][:100]}...")
        print("-" * 80)
    
    conn.close()

if __name__ == "__main__":
    verify_database()
