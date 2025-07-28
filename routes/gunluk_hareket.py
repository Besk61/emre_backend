# routes/gunluk_hareket.py
from flask import Blueprint, jsonify
from database import get_db_connection

gunluk_hareket_bp = Blueprint('gunluk_hareket_api', __name__)

@gunluk_hareket_bp.route('/', methods=['GET'])
def get_gunluk_hareket():
    conn = get_db_connection()
    # SQLite'ta GETDATE() -> date('now')
    query = """
      SELECT 
        SUM(CASE WHEN TURU = 'in' THEN ADET ELSE 0 END) AS giris,
        SUM(CASE WHEN TURU = 'out' THEN ADET ELSE 0 END) AS cikis
      FROM STOK_HAREKETLERI
      WHERE "ALMA-TARIHI" = date('now', 'localtime')
    """
    result = conn.execute(query).fetchone()
    conn.close()

    giris = result['giris'] if result['giris'] is not None else 0
    cikis = result['cikis'] if result['cikis'] is not None else 0
    net = giris - cikis
    
    return jsonify({"giris": giris, "cikis": cikis, "net": net})