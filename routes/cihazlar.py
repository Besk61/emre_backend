# routes/cihazlar.py
from flask import Blueprint, jsonify, request
from database import get_db_connection
import random
import string

cihazlar_bp = Blueprint('cihazlar_api', __name__)

@cihazlar_bp.route('/', methods=['GET'])
def get_cihazlar():
    conn = get_db_connection()
    # Orijinaldeki gibi tüm sütunları seçiyoruz
    cihazlar = conn.execute("SELECT *, `CIHAZ-KODU` as code FROM CIHAZLAR_YENI").fetchall()
    conn.close()
    return jsonify([dict(c) for c in cihazlar])

@cihazlar_bp.route('/', methods=['POST'])
def add_cihaz():
    data = request.get_json()
    if not data.get('name') or not data.get('category'):
        return jsonify({"error": "Cihaz kodu ve kategori alanları zorunludur."}), 400

    # 🔴 DÜZELTME: Barkod ve Seri No frontend'den gelmiyorsa otomatik üret.
    # Frontend'in gönderdiği anahtar 'seriNo' olabilir, Python'da 'seri_no' kullanmak daha yaygındır.
    # Anahtar isimlerine dikkat edelim. Frontend 'seriNumarasi' gönderiyor olabilir.
    
    # Güvenli erişim için data.get() kullanalım.
    barkod = data.get('barkod')
    if not barkod:
        barkod = f"BARKOD-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

    # Frontend'den 'seriNo' veya 'seriNumarasi' gelebilir, ikisini de kontrol edelim.
    seri_no = data.get('seriNo') or data.get('seriNumarasi')
    if not seri_no:
        seri_no = f"SERI-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"


    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CIHAZLAR_YENI ("CIHAZ-KODU", "CIHAZ-TIPI", ADET, minstok, FİYAT, SON_GUNCELLEME, BARKOD, "SERI-NUMARASI")
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
        """, (
            data['name'], data['category'], data.get('stock', 0), data.get('minStock', 0),
            data.get('price', 0), barkod, seri_no
        ))
        
        new_id = cursor.lastrowid
        conn.commit()
        
        # Eklenen yeni ürünü geri döndür
        new_product = {
            "id": new_id,
            "ID": new_id,
            "CIHAZ-KODU": data['name'],
            "CIHAZ-TIPI": data['category'],
            "ADET": data.get('stock', 0),
            "minstok": data.get('minStock', 0),
            "FİYAT": data.get('price', 0),
            "BARKOD": barkod,
            "SERI-NUMARASI": seri_no,
            "SON_GUNCELLEME": "Şimdi" # Gerçek zamanı da alabiliriz
        }
        
    except conn.IntegrityError:
        conn.close()
        return jsonify({"error": f"'{data['name']}' kodlu cihaz zaten mevcut."}), 409
    finally:
        conn.close()
        
    return jsonify(new_product), 201

@cihazlar_bp.route('/<string:code>', methods=['PUT'])
def update_cihaz(code):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("""
        UPDATE CIHAZLAR_YENI
        SET "CIHAZ-KODU" = ?, "CIHAZ-TIPI" = ?, ADET = ?, minstok = ?, FİYAT = ?,
            SON_GUNCELLEME = CURRENT_TIMESTAMP, BARKOD = ?, "SERI-NUMARASI" = ?
        WHERE "CIHAZ-KODU" = ?
    """, (
        data['name'], data['category'], data['stock'], data['minStock'], data['price'],
        data['barkod'], data['seriNo'], code
    ))
    conn.commit()
    conn.close()
    return "", 200

@cihazlar_bp.route('/<string:code>', methods=['DELETE'])
def delete_cihaz(code):
    conn = get_db_connection()
    try:
        # Cihaz ID'sini al
        cihaz = conn.execute('SELECT ID FROM CIHAZLAR_YENI WHERE "CIHAZ-KODU" = ?', (code,)).fetchone()
        if not cihaz:
            return jsonify({"error": "Cihaz bulunamadı"}), 404
        cihaz_id = str(cihaz['ID'])

        # HASTALAR tablosundan bu cihaz ID'sini temizle
        hastalar = conn.execute("SELECT ID, URUNLER FROM HASTALAR WHERE URUNLER LIKE ?", (f'%{cihaz_id}%',)).fetchall()
        for hasta in hastalar:
            urunler_list = [u.strip() for u in hasta['URUNLER'].split(',') if u.strip()]
            if cihaz_id in urunler_list:
                urunler_list.remove(cihaz_id)
                yeni_urunler = ','.join(urunler_list)
                conn.execute("UPDATE HASTALAR SET URUNLER = ? WHERE ID = ?", (yeni_urunler, hasta['ID']))

        # Son olarak cihazı sil
        conn.execute('DELETE FROM CIHAZLAR_YENI WHERE "CIHAZ-KODU" = ?', (code,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Silme hatası: {e}")
        return jsonify({"error": "Silme işlemi sırasında bir hata oluştu."}), 500
    finally:
        conn.close()
        
    return "", 200