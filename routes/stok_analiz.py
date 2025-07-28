# routes/stok_analiz.py
from flask import Blueprint, jsonify
from database import get_db_connection

stok_analiz_bp = Blueprint('stok_analiz_api', __name__)

@stok_analiz_bp.route('/', methods=['GET'])
def get_stok_analiz():
    conn = get_db_connection()
    analiz = conn.execute("""
        SELECT 
            "CIHAZ-TIPI" AS name,  
            SUM(ADET) AS stok     
        FROM CIHAZLAR_YENI
        GROUP BY "CIHAZ-TIPI"
    """).fetchall()
    conn.close()
    return jsonify([dict(a) for a in analiz])