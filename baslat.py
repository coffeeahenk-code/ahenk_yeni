"""Ahenk Coffee uygulamasının başlatma noktası."""
import os
from uygulama import uygulama_olustur

uygulama = uygulama_olustur()

if __name__ == "__main__":
    # Canlı ortamda debug modu kapalı olmalıdır.
    debug_acik = os.getenv("FLASK_ORTAMI", "gelistirme").lower() == "gelistirme"
    uygulama.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=debug_acik)
