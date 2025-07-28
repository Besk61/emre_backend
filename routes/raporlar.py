# routes/raporlar.py
from flask import Blueprint, jsonify
from database import get_db_connection

raporlar_bp = Blueprint('raporlar_api', __name__)

@raporlar_bp.route('/', methods=['GET'])
def get_stock_report():
    conn = get_db_connection()
    stock_data = conn.execute("""
        SELECT 
            "CIHAZ-KODU" AS cihazKodu, "CIHAZ-TIPI" AS cihazTipi,
            ADET AS adet, minstok AS minstok, FİYAT AS fiyat
        FROM CIHAZLAR_YENI
        WHERE ADET IS NOT NULL AND FİYAT IS NOT NULL
    """).fetchall()
    conn.close()
    
    rows = []
    total_value = 0
    total_count = 0

    for row_data in stock_data:
        row = dict(row_data) # Veritabanı satırını sözlüğe çevir
        adet = row.get('adet', 0)
        minstok = row.get('minstok', 0)
        fiyat = row.get('fiyat', 0)

        if adet <= minstok:
            status = 'critical' if adet == 0 else 'low'
        else:
            status = 'normal'
            
        value = adet * fiyat
        
        rows.append({
            "product": row['cihazKodu'],
            "category": row['cihazTipi'],
            "stock": adet,
            "minStock": minstok,
            "value": value,
            "status": status
        })
        total_value += value
        total_count += adet

    return jsonify({
        "stockReport": rows,
        "totalValue": total_value,
        "totalCount": total_count
    })


@raporlar_bp.route('/movement', methods=['GET'])
def get_movement_report():
    conn = get_db_connection()
    hareketler = conn.execute("""
        SELECT ID, "CIHAZ-TIPI", "CIHAZ-KODU", ADET, TURU, "ALMA-TARIHI", ACIKLAMA
        FROM STOK_HAREKETLERI
        ORDER BY "ALMA-TARIHI" DESC
    """).fetchall()
    conn.close()
    
    movement_report = []
    for row_data in hareketler:
        row = dict(row_data)
        movement_report.append({
            "date": row['ALMA-TARIHI'] if row['ALMA-TARIHI'] else "-",
            "type": "Giriş" if row['TURU'] == 'in' else "Çıkış",
            "product": row['CIHAZ-KODU'],
            "quantity": row['ADET'],
            "value": "-", # Bu veri orijinalinde de yoktu
            "reason": row['ACIKLAMA'] if row['ACIKLAMA'] else "-"
        })

    return jsonify(movement_report)