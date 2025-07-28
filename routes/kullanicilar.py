# routes/kullanicilar.py
from flask import Blueprint, jsonify, request
from database import get_db_connection

kullanicilar_bp = Blueprint('kullanicilar_api', __name__)

@kullanicilar_bp.route('/', methods=['GET'])
def get_kullanicilar():
    conn = get_db_connection()
    users = conn.execute("SELECT ID as id, ad || ' ' || soyad as name, rol, email, sifre as password FROM USERS").fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

@kullanicilar_bp.route('/', methods=['POST'])
def add_kullanici():
    data = request.get_json()
    ad, soyad = data['name'].split(' ', 1) if ' ' in data['name'] else (data['name'], '')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO USERS (ad, soyad, rol, sifre, email) VALUES (?, ?, ?, ?, ?)",
            (ad, soyad, data['role'], data['password'], data['email'])
        )
        new_id = cursor.lastrowid
        conn.commit()
    except conn.IntegrityError:
        conn.close()
        return jsonify({"error": "Bu e-posta adresi zaten kullanılıyor."}), 409
    finally:
        conn.close()
    
    return jsonify({'id': new_id, 'name': data['name'], 'role': data['role'], 'email': data['email']}), 201

@kullanicilar_bp.route('/<int:id>', methods=['DELETE'])
def delete_kullanici(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM USERS WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

@kullanicilar_bp.route('/<int:id>', methods=['PUT'])
def update_kullanici(id):
    data = request.get_json()
    ad, soyad = data['name'].split(' ', 1) if ' ' in data['name'] else (data['name'], '')
    conn = get_db_connection()
    conn.execute(
        "UPDATE USERS SET ad = ?, soyad = ?, email = ?, sifre = ?, rol = ? WHERE ID = ?",
        (ad, soyad, data['email'], data['password'], data['role'], id)
    )
    conn.commit()
    conn.close()
    return jsonify(data)

@kullanicilar_bp.route('/<int:id>/reset-password', methods=['POST'])
def reset_password(id):
    conn = get_db_connection()
    conn.execute("UPDATE USERS SET sifre = '123456' WHERE ID = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Şifre başarıyla sıfırlandı."}), 200