# routes/products.py
from flask import Blueprint, jsonify
from database import get_db_connection

products_bp = Blueprint('products_api', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    conn = get_db_connection()
    # COALESCE, ISNULL'un karşılığıdır.
    query = """
      SELECT 
        "CIHAZ-KODU" AS name,
        "CIHAZ-TIPI" AS category,
        COALESCE(ADET, 0) AS stock,
        COALESCE(FİYAT, 0) AS price,
        COALESCE(minstok, 0) AS minStock,
        COALESCE(SON_GUNCELLEME, '') AS lastUpdated
      FROM CIHAZLAR_YENI;
    """
    products = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])