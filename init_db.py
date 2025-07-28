# init_db.py
import sqlite3

# Tabloları silip yeniden oluşturmak için
conn = sqlite3.connect('stok.db')
cursor = conn.cursor()

print("Mevcut veritabanı temizleniyor ve yeniden oluşturuluyor...")

# Mevcut tabloları sil
cursor.execute("DROP TABLE IF EXISTS STOK_HAREKETLERI;")
cursor.execute("DROP TABLE IF EXISTS CIHAZLAR_YENI;")
cursor.execute("DROP TABLE IF EXISTS HASTALAR;")
cursor.execute("DROP TABLE IF EXISTS USERS;")
cursor.execute("DROP TABLE IF EXISTS TEDARIKCILER_YENI;")

# CIHAZLAR_YENI tablosu
# Not: Sütun adlarında '-' gibi özel karakterler varsa çift tırnak kullanmak en iyisidir.
cursor.execute("""
CREATE TABLE CIHAZLAR_YENI (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    "CIHAZ-KODU" TEXT NOT NULL UNIQUE,
    "CIHAZ-TIPI" TEXT,
    ADET INTEGER DEFAULT 0,
    minstok INTEGER DEFAULT 0,
    FİYAT REAL DEFAULT 0,
    SON_GUNCELLEME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    BARKOD TEXT,
    "SERI-NUMARASI" TEXT
);
""")

# USERS tablosu
cursor.execute("""
CREATE TABLE USERS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT,
    soyad TEXT,
    rol TEXT,
    email TEXT UNIQUE,
    sifre TEXT
);
""")

# HASTALAR tablosu
cursor.execute("""
CREATE TABLE HASTALAR (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    AD TEXT,
    SOYAD TEXT,
    KIMLIK_NO TEXT UNIQUE,
    URUNLER TEXT, -- '1,5,12' gibi cihaz ID'leri
    NOTLAR TEXT,
    KAYIT_TARIHI TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT
);
""")

# STOK_HAREKETLERI tablosu
cursor.execute("""
CREATE TABLE STOK_HAREKETLERI (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    "CIHAZ-TIPI" TEXT,
    "CIHAZ-KODU" TEXT,
    ADET INTEGER,
    TURU TEXT, -- 'in' veya 'out'
    "ALMA-TARIHI" DATE,
    SAAT TIME,
    ACIKLAMA TEXT,
    ALAN_HASTA INTEGER,
    VEREN INTEGER,
    FOREIGN KEY("CIHAZ-KODU") REFERENCES CIHAZLAR_YENI("CIHAZ-KODU") ON DELETE CASCADE,
    FOREIGN KEY(ALAN_HASTA) REFERENCES HASTALAR(ID) ON DELETE SET NULL,
    FOREIGN KEY(VEREN) REFERENCES USERS(ID) ON DELETE SET NULL
);
""")

# TEDARIKCILER_YENI tablosu (stats için gerekli)
cursor.execute("""
CREATE TABLE TEDARIKCILER_YENI (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    AD TEXT NOT NULL
);
""")

print("Tablolar başarıyla oluşturuldu. Örnek veriler ekleniyor...")

# Örnek Veri Ekleme
cursor.execute("INSERT INTO USERS (ad, soyad, rol, email, sifre) VALUES ('Admin', 'Kullanıcı', 'admin', 'admin@stok.com', 'sifre123');")
cursor.execute("INSERT INTO TEDARIKCILER_YENI (AD) VALUES ('Medikal A.Ş.');")
cursor.execute("INSERT INTO TEDARIKCILER_YENI (AD) VALUES ('Sağlık Lojistik');")

cursor.execute("INSERT INTO HASTALAR (AD, SOYAD, KIMLIK_NO, status) VALUES ('Ahmet', 'Yılmaz', '11111111111', 'aktif');")
cursor.execute("INSERT INTO HASTALAR (AD, SOYAD, KIMLIK_NO, status) VALUES ('Ayşe', 'Kaya', '22222222222', 'pasif');")

cursor.execute("""
INSERT INTO CIHAZLAR_YENI ("CIHAZ-KODU", "CIHAZ-TIPI", ADET, minstok, FİYAT, BARKOD, "SERI-NUMARASI") 
VALUES ('CPAP-01', 'Solunum Cihazı', 15, 5, 1850.75, 'BARKOD-CPAP01', 'SERI-CPAP01');
""")
cursor.execute("""
INSERT INTO CIHAZLAR_YENI ("CIHAZ-KODU", "CIHAZ-TIPI", ADET, minstok, FİYAT, BARKOD, "SERI-NUMARASI") 
VALUES ('MON-01', 'Hasta Monitörü', 8, 3, 3200.00, 'BARKOD-MON01', 'SERI-MON01');
""")
cursor.execute("""
INSERT INTO CIHAZLAR_YENI ("CIHAZ-KODU", "CIHAZ-TIPI", ADET, minstok, FİYAT, BARKOD, "SERI-NUMARASI") 
VALUES ('ASP-03', 'Aspiratör', 2, 2, 750.00, 'BARKOD-ASP03', 'SERI-ASP03');
""")

# Örnek Stok Hareketi
cursor.execute("""
INSERT INTO STOK_HAREKETLERI ("CIHAZ-TIPI", "CIHAZ-KODU", ADET, TURU, "ALMA-TARIHI", SAAT, ACIKLAMA, ALAN_HASTA, VEREN)
VALUES ('Solunum Cihazı', 'CPAP-01', 1, 'out', date('now', '-1 day'), time('now'), 'Hasta teslimatı', 1, 1);
""")


conn.commit()
conn.close()

print("✅ Veritabanı kurulumu tamamlandı.")
print("Terminalde 'python app.py' komutu ile sunucuyu başlatabilirsiniz.")