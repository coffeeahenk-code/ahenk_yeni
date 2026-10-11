"""Ahenk kahve rehberi: Groq API bağlantısı, demo yanıtları ve hata ayrıştırma."""
import logging
import requests
from flask import current_app
from uygulama.hatalar import YapayZekaServisHatasi

logger = logging.getLogger(__name__)

class AhenkYapayZekaServisi:
    def yanit_uret(self, mesaj, gecmis=None):
        saglayici = current_app.config.get("AI_PROVIDER", "groq").lower()
        if saglayici != "groq":
            raise YapayZekaServisHatasi("AI-001", "Yapılandırılmış yapay zekâ sağlayıcısı desteklenmiyor.", f"Desteklenmeyen AI_PROVIDER: {saglayici}", 503)
        anahtar = current_app.config.get("GROQ_API_KEY", "").strip()
        if not anahtar:
            logger.info("AI-002: GROQ_API_KEY tanımlı değil; demo yanıtı döndürülüyor.")
            return self._demo_yaniti_ver(mesaj)
        return self._groq_cagir(mesaj, gecmis or [], anahtar)

    def _groq_cagir(self, mesaj, gecmis, anahtar):
        cfg = current_app.config
        iletiler = [{"role": "system", "content": cfg["BUSINESS_CONTEXT"]}]
        # Geçmiş sadece son 10 iletiyle sınırlandırılır ve rol listesi doğrulanır.
        for ileti in gecmis[-10:]:
            if isinstance(ileti, dict) and ileti.get("role") in ("user", "assistant") and isinstance(ileti.get("content"), str):
                iletiler.append({"role": ileti["role"], "content": ileti["content"][:2000]})
        iletiler.append({"role": "user", "content": mesaj})
        try:
            yanit = requests.post(
                cfg["GROQ_API_URL"],
                headers={"Authorization": f"Bearer {anahtar}", "Content-Type": "application/json"},
                json={"model": cfg["GROQ_MODEL"], "messages": iletiler, "temperature": 0.6, "max_tokens": 700},
                timeout=cfg["AI_TIMEOUT_SECONDS"],
            )
        except requests.Timeout as exc:
            logger.warning("AI-003: Groq zaman aşımına uğradı.")
            raise YapayZekaServisHatasi("AI-003", "Kahve rehberimiz yanıt vermekte gecikti. Lütfen tekrar deneyin.", "Groq isteği zaman aşımına uğradı.", 503) from exc
        except requests.ConnectionError as exc:
            logger.warning("AI-004: Groq bağlantısı kurulamadı: %s", exc)
            raise YapayZekaServisHatasi("AI-004", "Yapay zekâ servisine bağlanılamıyor. İnternet bağlantısını daha sonra tekrar deneyin.", f"Groq bağlantı hatası: {exc}", 503) from exc
        except requests.RequestException as exc:
            logger.exception("AI-005: HTTP isteği sırasında hata oluştu.")
            raise YapayZekaServisHatasi("AI-005", "Yapay zekâ isteği tamamlanamadı.", f"HTTP isteği hatası: {exc}", 503) from exc

        if yanit.status_code == 401 or yanit.status_code == 403:
            logger.error("AI-006: Groq kimlik doğrulaması reddedildi (HTTP %s).", yanit.status_code)
            raise YapayZekaServisHatasi("AI-006", "Yapay zekâ bağlantı ayarı doğrulanamadı. API anahtarını kontrol edin.", f"Groq kimlik doğrulama hatası: HTTP {yanit.status_code}", 503)
        if yanit.status_code == 404:
            logger.error("AI-007: Groq modeli veya endpoint bulunamadı. Model=%s", cfg["GROQ_MODEL"])
            raise YapayZekaServisHatasi("AI-007", "Yapay zekâ modeli bulunamadı. GROQ_MODEL ayarını kontrol edin.", f"Groq 404; model={cfg['GROQ_MODEL']}", 503)
        if yanit.status_code == 429:
            logger.warning("AI-008: Groq istek sınırına ulaşıldı.")
            raise YapayZekaServisHatasi("AI-008", "Kahve rehberimize kısa sürede çok fazla istek geldi. Biraz bekleyip tekrar deneyin.", "Groq HTTP 429 rate limit.", 429)
        if yanit.status_code >= 500:
            logger.error("AI-009: Groq sunucu hatası (HTTP %s).", yanit.status_code)
            raise YapayZekaServisHatasi("AI-009", "Yapay zekâ sağlayıcısında geçici bir sorun var. Lütfen daha sonra tekrar deneyin.", f"Groq sunucu hatası: HTTP {yanit.status_code}", 503)
        if not yanit.ok:
            logger.error("AI-010: Groq isteği reddedildi (HTTP %s).", yanit.status_code)
            raise YapayZekaServisHatasi("AI-010", "Yapay zekâ isteği kabul edilmedi. Model ve istek ayarlarını kontrol edin.", f"Groq istemci hatası: HTTP {yanit.status_code}; body={yanit.text[:500]}", 503)
        try:
            veri = yanit.json()
            cevap = veri["choices"][0]["message"]["content"]
            if not isinstance(cevap, str) or not cevap.strip():
                raise ValueError("Yanıt metni boş veya metin biçiminde değil.")
            return cevap.strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            logger.exception("AI-011: Groq yanıtı beklenen biçimde değil.")
            raise YapayZekaServisHatasi("AI-011", "Yapay zekâdan okunabilir bir yanıt alınamadı. Lütfen tekrar deneyin.", f"Groq yanıt biçimi hatası: {exc}", 502) from exc

    def _demo_yaniti_ver(self, mesaj):
        """API anahtarı olmadan arayüzü test etmeyi sağlayan açıkça etiketli demo modu."""
        metin = mesaj.lower()
        if any(k in metin for k in ("espresso", "espresso")):
            oner = "Espresso, yoğun aromalı ve küçük hacimli bir kahvedir. Sütlü içeceklerin de temelini oluşturur."
        elif any(k in metin for k in ("türkiye", "türk kahvesi", "turkish")):
            oner = "Türk kahvesi, ince öğütülmüş kahvenin suyla cezvede pişirilmesiyle hazırlanır; köpüğü ve telvesiyle kendine özgü bir deneyim sunar."
        elif any(k in metin for k in ("kolombiya", "colombia")):
            oner = "Kolombiya kahveleri çoğunlukla dengeli gövde ve meyvemsi ya da karamelimsi notalarla anılır; tat profili bölgeye ve işleme yöntemine göre değişir."
        else:
            oner = "Ahenk'te kahveyi yalnızca bir içecek değil, farklı kültürleri tanımanın keyifli bir yolu olarak görüyoruz. İsterseniz Türk kahvesi, espresso veya filtre kahve üzerinden keşfe başlayabiliriz."
        return f"[DEMO MODU — gerçek yapay zekâ bağlantısı etkin değil]\n\n{oner}\n\nGerçek AI yanıtları için .env dosyasına geçerli bir GROQ_API_KEY ekleyin."


yapay_zeka_servisi = AhenkYapayZekaServisi()
