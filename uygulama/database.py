"""SQLite erişimi. SQL sorgularında kullanıcı verileri parametre olarak geçirilir."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from uygulama.hatalar import VeritabaniHatasi


def baglanti_al(database_path):
    try:
        yol = Path(database_path)
        yol.parent.mkdir(parents=True, exist_ok=True)
        baglanti = sqlite3.connect(str(yol), timeout=10)
        baglanti.row_factory = sqlite3.Row
        baglanti.execute("PRAGMA foreign_keys = ON")
        return baglanti
    except (OSError, sqlite3.Error) as exc:
        raise VeritabaniHatasi("DB-002", "Kayıt sistemine şu anda ulaşılamıyor.", f"Veritabanı bağlantı hatası: {exc}", 500) from exc


def veritabani_baslat(database_path):
    baglanti = baglanti_al(database_path)
    try:
        baglanti.execute("""CREATE TABLE IF NOT EXISTS iletisim_kayitlari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            eposta TEXT NOT NULL,
            ulke TEXT NOT NULL DEFAULT '',
            mesaj TEXT NOT NULL DEFAULT '',
            izin_verildi INTEGER NOT NULL DEFAULT 0,
            olusturulma_tarihi TEXT NOT NULL
        )""")
        baglanti.commit()
    except sqlite3.Error as exc:
        baglanti.rollback()
        raise VeritabaniHatasi("DB-003", "Veritabanı hazırlanamadı.", f"Tablo oluşturma hatası: {exc}", 500) from exc
    finally:
        baglanti.close()


def iletisim_kaydi_ekle(database_path, isim, eposta, ulke, mesaj, izin_verildi):
    baglanti = baglanti_al(database_path)
    try:
        tarih = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cursor = baglanti.execute(
            "INSERT INTO iletisim_kayitlari (isim, eposta, ulke, mesaj, izin_verildi, olusturulma_tarihi) VALUES (?, ?, ?, ?, ?, ?)",
            (isim, eposta, ulke, mesaj, int(izin_verildi), tarih),
        )
        baglanti.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        baglanti.rollback()
        raise VeritabaniHatasi("DB-004", "Bilgiler kaydedilemedi; girdiğiniz alanları kontrol edin.", f"Kayıt kısıt ihlali: {exc}", 400) from exc
    except sqlite3.Error as exc:
        baglanti.rollback()
        raise VeritabaniHatasi("DB-005", "Bilgiler şu anda kaydedilemedi. Lütfen tekrar deneyin.", f"Kayıt ekleme hatası: {exc}", 500) from exc
    finally:
        baglanti.close()


def tum_kayitlari_getir(database_path, arama=""):
    baglanti = baglanti_al(database_path)
    try:
        if arama:
            desen = f"%{arama}%"
            rows = baglanti.execute(
                "SELECT id, isim, eposta, ulke, mesaj, izin_verildi, olusturulma_tarihi FROM iletisim_kayitlari WHERE isim LIKE ? OR eposta LIKE ? OR ulke LIKE ? ORDER BY id DESC LIMIT 500",
                (desen, desen, desen),
            ).fetchall()
        else:
            rows = baglanti.execute("SELECT id, isim, eposta, ulke, mesaj, izin_verildi, olusturulma_tarihi FROM iletisim_kayitlari ORDER BY id DESC LIMIT 500").fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise VeritabaniHatasi("DB-006", "Kayıtlar şu anda listelenemiyor.", f"Kayıt listeleme hatası: {exc}", 500) from exc
    finally:
        baglanti.close()

def iletisim_kaydi_sil(database_path, kayit_id):
    baglanti = baglanti_al(database_path)
    try:
        cursor = baglanti.execute(
            "DELETE FROM iletisim_kayitlari WHERE id = ?",
            (kayit_id,)
        )
        baglanti.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as exc:
        baglanti.rollback()
        raise VeritabaniHatasi(
            "DB-007",
            "Kayıt silinemedi.",
            f"Kayıt silme hatası: {exc}",
            500
        ) from exc
    finally:
        baglanti.close()


def rezervasyon_kaydi_ekle(database_path, isim, telefon, eposta, kisi_sayisi, notlar):
    baglanti = baglanti_al(database_path)
    try:
        cursor = baglanti.execute(
            """INSERT INTO rezervasyon_kayitlari
            (isim, telefon, eposta, kisi_sayisi, notlar, olusturulma_tarihi)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                isim, telefon, eposta, kisi_sayisi, notlar,
                datetime.now(timezone.utc).isoformat(timespec="seconds")
            )
        )
        baglanti.commit()
        return cursor.lastrowid
    finally:
        baglanti.close()


def rezervasyonlari_getir(database_path):
    baglanti = baglanti_al(database_path)
    try:
        rows = baglanti.execute(
            """SELECT id, isim, telefon, eposta,
                      kisi_sayisi, notlar, olusturulma_tarihi
               FROM rezervasyon_kayitlari
               ORDER BY id DESC LIMIT 500"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        baglanti.close()

