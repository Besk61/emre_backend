# routes/hastalar.py
from flask import Blueprint, jsonify, request
from database import get_db_connection

hastalar_bp = Blueprint('hastalar_api', __name__)

@hastalar_bp.route('/', methods=['GET'])
def get_hastalar():
    conn = get_db_connection()
    hastalar = conn.execute("SELECT ID, AD, SOYAD, KIMLIK_NO, URUNLER, NOTLAR, KAYIT_TARIHI, status FROM HASTALAR").fetchall()
    conn.close()
    return jsonify([dict(h) for h in hastalar])

@hastalar_bp.route('/', methods=['POST'])
def add_hasta():
    data = request.get_json()
    if not all(k in data for k in ['AD', 'SOYAD', 'KIMLIK_NO']):
        return jsonify({"error": "AD, SOYAD ve KIMLIK_NO alanları zorunludur."}), 400

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO HASTALAR (AD, SOYAD, KIMLIK_NO, URUNLER, NOTLAR, KAYIT_TARIHI, status)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """, (
            data['AD'], data['SOYAD'], data['KIMLIK_NO'], data.get('URUNLER', ''), 
            data.get('NOTLAR', ''), data.get('status', 'pasif')
        ))
        conn.commit()
    except conn.IntegrityError:
        conn.close()
        return jsonify({"error": "Bu kimlik numarasına sahip bir hasta zaten kayıtlı."}), 409
    finally:
        conn.close()
    return jsonify({"message": "Hasta başarıyla eklendi"}), 201

@hastalar_bp.route('/<int:id>', methods=['DELETE'])
def delete_hasta(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM HASTALAR WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Hasta silindi"}), 200

@hastalar_bp.route('/<int:id>', methods=['PUT'])
def update_hasta(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("""
        UPDATE HASTALAR SET AD = ?, SOYAD = ?, KIMLIK_NO = ?, URUNLER = ?, NOTLAR = ?, status = ?
        WHERE ID = ?
    """, (
        data['AD'], data['SOYAD'], data['KIMLIK_NO'], data['URUNLER'], 
        data['NOTLAR'], data['status'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Hasta güncellendi"}), 200

@hastalar_bp.route('/devices', methods=['GET'])
def get_hasta_cihazlari():
    conn = get_db_connection()
    cihazlar = conn.execute("SELECT ID, \"CIHAZ-KODU\" as kod FROM CIHAZLAR_YENI").fetchall()
    conn.close()
    return jsonify([dict(c) for c in cihazlar])