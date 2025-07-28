# database.py
import sqlite3

DATABASE_NAME = 'stok.db'

def get_db_connection():
    """Veritabanı bağlantısı oluşturur ve satırları sözlük gibi döndürmesini sağlar."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Bu satır, veritabanından gelen sonuçları sütun adlarıyla erişilebilir hale getirir.
    conn.row_factory = sqlite3.Row
    return conn