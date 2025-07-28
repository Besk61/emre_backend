# routes/kritik_stok.py
from flask import Blueprint, jsonify
from database import get_db_connection

kritik_stok_bp = Blueprint('kritik_stok_api', __name__)

@kritik_stok_bp.route('/', methods=['GET'])
def get_kritik_stok():
    conn = get_db_connection()
    stok = conn.execute("""
        SELECT 
            ID, "CIHAZ-KODU" AS name, ADET AS currentStock, 
            minstok AS minStock, "CIHAZ-TIPI" AS category
        FROM CIHAZLAR_YENI
        WHERE ADET <= minstok
    """).fetchall()
    conn.close()
    return jsonify([dict(s) for s in stok])