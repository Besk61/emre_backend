# routes/hareketler.py
from flask import Blueprint, jsonify, request
from database import get_db_connection
from datetime import datetime

hareketler_bp = Blueprint('hareketler_api', __name__)

@hareketler_bp.route('/', methods=['GET'])
def get_stok_hareketleri():
    conn = get_db_connection()
    # SQLite'ta string birleştirme '||' ile yapılır.
    query = """
      SELECT 
        SH.ID, SH."CIHAZ-KODU", SH."CIHAZ-TIPI", SH.ADET, SH.TURU, SH."ALMA-TARIHI", SH.SAAT,
        SH."ALMA-TARIHI" || ' ' || substr(SH.SAAT, 1, 8) AS TAM_TARIH_SAAT,
        SH.ACIKLAMA, CY.FİYAT, SH.ALAN_HASTA as alanHastaId, SH.VEREN,
        H.AD || ' ' || H.SOYAD AS HASTA_ADI 
      FROM STOK_HAREKETLERI SH
      LEFT JOIN CIHAZLAR_YENI CY ON SH."CIHAZ-KODU" = CY."CIHAZ-KODU"
      LEFT JOIN HASTALAR H ON SH.ALAN_HASTA = H.ID
    """
    
    params = []
    start = request.args.get('start')
    end = request.args.get('end')
    
    conditions = []
    if start:
        conditions.append('SH."ALMA-TARIHI" >= ?')
        params.append(start)
    if end:
        # Bitiş tarihini de dahil etmek için
        conditions.append('SH."ALMA-TARIHI" <= ?')
        params.append(end)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY SH.\"ALMA-TARIHI\" DESC, SH.SAAT DESC"

    hareketler = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(h) for h in hareketler])

@hareketler_bp.route('/hareket', methods=['POST'])
def add_stok_hareketi():
    data = request.get_json()
    cihaz_kodu = data['cihazKodu']
    hareket_tipi = data['hareketTipi']
    miktar = int(data['miktar'])
    
    conn = get_db_connection()
    try:
        cihaz = conn.execute('SELECT * FROM CIHAZLAR_YENI WHERE "CIHAZ-KODU" = ?', (cihaz_kodu,)).fetchone()
        if not cihaz:
            return jsonify({"message": "Cihaz bulunamadı"}), 404

        mevcut_adet = cihaz['ADET'] if cihaz['ADET'] else 0
        yeni_adet = mevcut_adet + miktar if hareket_tipi == 'in' else mevcut_adet - miktar

        if yeni_adet < 0:
            return jsonify({"message": "Stok yetersiz. Çıkış yapılamaz."}), 400

        conn.execute('UPDATE CIHAZLAR_YENI SET ADET = ? WHERE "CIHAZ-KODU" = ?', (yeni_adet, cihaz_kodu))

        now = datetime.now()
        tarih = data.get('tarih', now.strftime('%Y-%m-%d'))
        saat = data.get('saat', now.strftime('%H:%M:%S'))

        conn.execute("""
            INSERT INTO STOK_HAREKETLERI ("CIHAZ-TIPI", "CIHAZ-KODU", ADET, TURU, "ALMA-TARIHI", SAAT, ACIKLAMA, ALAN_HASTA, VEREN)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('cihazTipi'), cihaz_kodu, miktar, hareket_tipi, tarih, saat,
            data.get('aciklama'), data.get('alanHasta'), data.get('veren')
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Hata: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
    return jsonify({"message": "Hareket başarıyla kaydedildi."}), 200