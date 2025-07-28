# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS

# Rota Blueprint'lerini import et
from routes.cihazlar import cihazlar_bp
from routes.stats import stats_bp
from routes.products import products_bp
from routes.cihaz_tipleri import cihaz_tipleri_bp
from routes.hastalar import hastalar_bp
from routes.hareketler import hareketler_bp
from routes.raporlar import raporlar_bp
from routes.kritik_stok import kritik_stok_bp
from routes.gunluk_hareket import gunluk_hareket_bp
from routes.kullanicilar import kullanicilar_bp
from routes.movement_chart import movement_chart_bp
from routes.stok_analiz import stok_analiz_bp


app = Flask(__name__)
# 🔴 YENİ: strict_slashes=False tüm uygulama için ayarlanabilir.
# Bu, /rota ve /rota/ adreslerinin aynı şekilde davranmasını sağlar.
app.url_map.strict_slashes = False
port = 5000

# Orijin tanımı (CORS)
# CORS(app, 
#     resources={r"/*": {"origins": "http://localhost:5173"}}, 
#     supports_credentials=True,
#     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] # OPTIONS metodunu eklemek önemlidir
# )

CORS(app) # Tüm domainlerden erişime izin verir, üretimde kısıtlanabilir
# Gelen tüm istekleri logla (debug için)
@app.before_request
def log_request_info():
    print(f'[{request.method}] {request.url}')
    if request.data:
        print(f"Body: {request.get_json(silent=True)}")


# Genel hata yakalayıcı
@app.errorhandler(Exception)
def handle_exception(e):
    # Gerçek hata detayını konsola yazdır
    import traceback
    traceback.print_exc()
    # İstemciye genel bir hata mesajı gönder
    response = {
        "error": "Sunucuda bir hata oluştu. Lütfen daha sonra tekrar deneyin."
    }
    return jsonify(response), 500


# Tüm Blueprint'leri (route gruplarını) uygulamaya kaydet
app.register_blueprint(cihazlar_bp, url_prefix='/cihazlar')
app.register_blueprint(stats_bp, url_prefix='/stats')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(cihaz_tipleri_bp, url_prefix='/cihazTipleri')
app.register_blueprint(hastalar_bp, url_prefix='/patients')
app.register_blueprint(hareketler_bp, url_prefix='/stock')
app.register_blueprint(raporlar_bp, url_prefix='/reports')
app.register_blueprint(kritik_stok_bp, url_prefix='/kritikStok')
app.register_blueprint(gunluk_hareket_bp, url_prefix='/gunlukHareket')
app.register_blueprint(kullanicilar_bp, url_prefix='/users')
app.register_blueprint(movement_chart_bp, url_prefix='/movementChart')
app.register_blueprint(stok_analiz_bp, url_prefix='/stokAnaliz')


if __name__ == '__main__':
    print(f"✅ API http://localhost:{port} üzerinden çalışıyor")
    app.run(port=port, debug=True)