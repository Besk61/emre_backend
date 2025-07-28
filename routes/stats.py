# routes/stats.py
from flask import Blueprint, jsonify
from database import get_db_connection

stats_bp = Blueprint('stats_api', __name__)

@stats_bp.route('/', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    # Tek bir sorguda tüm istatistikleri alalım.
    query = """
    SELECT
        (SELECT SUM(ADET) FROM CIHAZLAR_YENI) AS toplamUrun,
        (SELECT COUNT(*) FROM CIHAZLAR_YENI WHERE ADET <= minstok) AS kritikStok,
        (SELECT SUM(ADET * FİYAT) FROM CIHAZLAR_YENI) AS toplamDeger,
        (SELECT COUNT(*) FROM TEDARIKCILER_YENI) AS tedarikciSayisi;
    """
    stats = conn.execute(query).fetchone()
    conn.close()
    
    if stats:
        # Sonuç None gelirse 0 döndür
        result_dict = {
            "toplamUrun": stats["toplamUrun"] or 0,
            "kritikStok": stats["kritikStok"] or 0,
            "toplamDeger": stats["toplamDeger"] or 0,
            "tedarikciSayisi": stats["tedarikciSayisi"] or 0,
        }
        return jsonify(result_dict)
    else:
        return jsonify({
            "toplamUrun": 0, "kritikStok": 0, "toplamDeger": 0, "tedarikciSayisi": 0
        })