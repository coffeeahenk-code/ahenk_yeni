"""Ahenk uygulamasının merkezi ayarları. Gizli anahtarlar .env dosyasından okunur."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJE_KOKU = Path(__file__).resolve().parent
load_dotenv(PROJE_KOKU / ".env")

class TemelAyarlar:
    SECRET_KEY = os.getenv("SECRET_KEY", "yalnizca-gelistirme-icin-degistir")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(PROJE_KOKU / "veri" / "ahenk.db"))
    FLASK_ORTAMI = os.getenv("FLASK_ORTAMI", "gelistirme").lower()
    DEBUG = FLASK_ORTAMI == "gelistirme"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "25"))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    JSON_SORT_KEYS = False
    BUSINESS_CONTEXT = """Sen Ahenk Coffee markasının nazik, bilgili ve samimi kahve rehberisin.
Ahenk; farklı ülkelerin kendine özgü kahvelerini ve kahve kültürlerini keşfetmek isteyen
kahve severleri bir araya getiren bir kafe markasıdır. Keşif, kahve kültürü, farklı kültürleri
tanıma ve sıcak bir deneyim değerlerini yansıt. Türkçe yanıt ver. Kahve türleri, demleme
 yöntemleri ve kültürel bağlam hakkında yardımcı ol. Menüde veya stokta olduğuna dair
 doğrulanmamış iddialarda bulunma; emin değilsen bunu açıkça belirt. Sağlıkla ilgili kesin
iddialar veya gerçek olmayan fiyatlar üretme. Gerektiğinde kullanıcıyı işletmeyle iletişime yönlendir."""

class GelistirmeAyarlari(TemelAyarlar):
    DEBUG = True

class UretimAyarlari(TemelAyarlar):
    DEBUG = False

AYAR_SECENEKLERI = {
    "gelistirme": GelistirmeAyarlari,
    "uretim": UretimAyarlari,
}
