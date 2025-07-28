# routes/movement_chart.py
from flask import Blueprint, jsonify
from database import get_db_connection

movement_chart_bp = Blueprint('movement_chart_api', __name__)

@movement_chart_bp.route('/', methods=['GET'])
def get_movement_chart_data():
    conn = get_db_connection()
    # SQLite'ta DATEADD -> date('now', '-6 days')
    # CONVERT(varchar, date, 23) -> strftime('%Y-%m-%d', date)
    query = """
      SELECT 
        strftime('%Y-%m-%d', "ALMA-TARIHI") AS tarih,
        SUM(CASE WHEN TURU = 'in' THEN ADET ELSE 0 END) AS giris,
        SUM(CASE WHEN TURU = 'out' THEN ADET ELSE 0 END) AS cikis
      FROM STOK_HAREKETLERI
      WHERE "ALMA-TARIHI" >= date('now', '-6 days')
      GROUP BY tarih
      ORDER BY tarih
    """
    data = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])