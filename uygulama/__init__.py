"""Flask uygulama fabrikası: ayarları, veritabanını ve rotaları birleştirir."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask, jsonify, render_template
from ayarlar import AYAR_SECENEKLERI, PROJE_KOKU
from uygulama.database import veritabani_baslat
from uygulama.hatalar import AhenkHatasi


def _loglama_kur(uygulama):
    """Logları konsola ve boyutu sınırlı dosyaya yazar; gizli anahtarları loglamayın."""
    log_klasoru = PROJE_KOKU / "loglar"
    try:
        log_klasoru.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(log_klasoru / "ahenk.log", maxBytes=500_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        handler.setLevel(logging.INFO)
        uygulama.logger.addHandler(handler)
    except OSError:
        # Log dosyası açılamazsa uygulamanın başlamasını engelleme; konsol logu sürsün.
        uygulama.logger.exception("LOG-001: Log dosyası hazırlanamadı; konsol loglaması kullanılacak.")
    if not uygulama.logger.handlers:
        logging.basicConfig(level=logging.INFO)


def uygulama_olustur(ayar_adi=None):
    uygulama = Flask(__name__, template_folder="sablonlar", static_folder="static")
    secilen = AYAR_SECENEKLERI.get(ayar_adi or __import__("os").getenv("FLASK_ORTAMI", "gelistirme"), AYAR_SECENEKLERI["gelistirme"])
    uygulama.config.from_object(secilen)
    _loglama_kur(uygulama)

    try:
        veritabani_baslat(uygulama.config["DATABASE_PATH"])
    except (OSError, RuntimeError) as exc:
        uygulama.logger.exception("DB-001: Başlangıçta veritabanı hazırlanamadı: %s", exc)
        raise RuntimeError("DB-001: Veritabanı başlatılamadı. DATABASE_PATH değerini ve klasör yazma izinlerini kontrol edin.") from exc

    from uygulama.rotalar import sayfa_arayuzu, api_arayuzu
    uygulama.register_blueprint(sayfa_arayuzu)
    uygulama.register_blueprint(api_arayuzu, url_prefix="/api")

    @uygulama.errorhandler(AhenkHatasi)
    def ahenk_hatasi_yakala(exc):
        uygulama.logger.warning("%s: %s", exc.kod, exc.log_mesaji)
        return jsonify({"basari": False, "hata": exc.kullanici_mesaji, "hata_kodu": exc.kod}), exc.http_durumu

    @uygulama.errorhandler(404)
    def bulunamadi(_exc):
        return jsonify({"basari": False, "hata": "İstenen adres bulunamadı.", "hata_kodu": "HTTP-404"}), 404

    @uygulama.errorhandler(405)
    def metod_yanlis(_exc):
        return jsonify({"basari": False, "hata": "Bu adreste bu istek türü desteklenmiyor.", "hata_kodu": "HTTP-405"}), 405

    @uygulama.errorhandler(Exception)
    def beklenmeyen_hata(exc):
        # İstemciye traceback veya sistem ayrıntısı gösterilmez; ayrıntı sunucu loguna yazılır.
        uygulama.logger.exception("SYS-500: Yakalanmamış uygulama hatası: %s", exc)
        return jsonify({"basari": False, "hata": "Beklenmeyen bir sorun oluştu. Lütfen daha sonra tekrar deneyin.", "hata_kodu": "SYS-500"}), 500

    return uygulama
