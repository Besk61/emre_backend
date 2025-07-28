# routes/cihaz_tipleri.py
from flask import Blueprint, jsonify
from database import get_db_connection

cihaz_tipleri_bp = Blueprint('cihaz_tipleri_api', __name__)

@cihaz_tipleri_bp.route('/', methods=['GET'])
def get_cihaz_tipleri():
    conn = get_db_connection()
    # COALESCE, ISNULL'un SQLite karşılığıdır.
    query = """
      SELECT 
        "CIHAZ-TIPI" AS name,
        COUNT(*) AS productCount,
        COALESCE(SUM(ADET), 0) AS productQuantity
      FROM CIHAZLAR_YENI
      WHERE "CIHAZ-TIPI" IS NOT NULL
      GROUP BY "CIHAZ-TIPI"
    """
    tipler = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(t) for t in tipler])