
"""Ahenk Coffee yapay zekâ servisi: Groq API ve demo yanıtları."""

import logging
import requests
from flask import current_app
from uygulama.hatalar import YapayZekaServisHatasi

logger = logging.getLogger(__name__)


class AhenkYapayZekaServisi:

    def yanit_uret(self, mesaj, gecmis=None):
        # AI_PROVIDER kontrolü kaldırıldı.
        # API anahtarı varsa Groq, yoksa demo yanıtı kullanılır.
        anahtar = current_app.config.get("GROQ_API_KEY", "").strip()

        if not anahtar:
            logger.warning(
                "GROQ_API_KEY tanımlı değil; demo yanıtı döndürülüyor."
            )
            return self._demo_yaniti_ver(mesaj)

        return self._groq_cagir(mesaj, gecmis or [], anahtar)

    def _groq_cagir(self, mesaj, gecmis, anahtar):
        cfg = current_app.config

        iletiler = [
            {
                "role": "system",
                "content": cfg["BUSINESS_CONTEXT"]
            }
        ]

        # Son 10 geçerli iletiyi kullan.
        for ileti in gecmis[-10:]:
            if (
                isinstance(ileti, dict)
                and ileti.get("role") in ("user", "assistant")
                and isinstance(ileti.get("content"), str)
            ):
                iletiler.append({
                    "role": ileti["role"],
                    "content": ileti["content"][:2000]
                })

        iletiler.append({
            "role": "user",
            "content": mesaj
        })

        try:
            yanit = requests.post(
                cfg["GROQ_API_URL"],
                headers={
                    "Authorization": f"Bearer {anahtar}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": cfg["GROQ_MODEL"],
                    "messages": iletiler,
                    "temperature": 0.6,
                    "max_tokens": 700
                },
                timeout=cfg["AI_TIMEOUT_SECONDS"]
            )

        except requests.Timeout as exc:
            logger.warning("Groq isteği zaman aşımına uğradı.")
            raise YapayZekaServisHatasi(
                "AI-003",
                "Kahve rehberimiz yanıt vermekte gecikti. Lütfen tekrar deneyin.",
                "Groq isteği zaman aşımına uğradı.",
                503
            ) from exc

        except requests.ConnectionError as exc:
            logger.warning("Groq bağlantısı kurulamadı.")
            raise YapayZekaServisHatasi(
                "AI-004",
                "Yapay zekâ servisine bağlanılamıyor. Lütfen daha sonra tekrar deneyin.",
                f"Groq bağlantı hatası: {exc}",
                503
            ) from exc

        except requests.RequestException as exc:
            logger.exception("Groq HTTP isteği başarısız.")
            raise YapayZekaServisHatasi(
                "AI-005",
                "Yapay zekâ isteği tamamlanamadı.",
                f"HTTP isteği hatası: {exc}",
                503
            ) from exc

        if yanit.status_code in (401, 403):
            logger.error("Groq kimlik doğrulaması başarısız: HTTP %s",
                         yanit.status_code)
            raise YapayZekaServisHatasi(
                "AI-006",
                "Yapay zekâ bağlantı ayarı doğrulanamadı. API anahtarını kontrol edin.",
                f"Groq HTTP {yanit.status_code}",
                503
            )

        if yanit.status_code == 404:
            logger.error("Groq modeli veya endpoint bulunamadı.")
            raise YapayZekaServisHatasi(
                "AI-007",
                "Yapay zekâ modeli bulunamadı. GROQ_MODEL ayarını kontrol edin.",
                f"Groq 404; model={cfg['GROQ_MODEL']}",
                503
            )

        if yanit.status_code == 429:
            raise YapayZekaServisHatasi(
                "AI-008",
                "Kahve rehberimize kısa sürede çok fazla istek geldi. Biraz bekleyip tekrar deneyin.",
                "Groq HTTP 429 rate limit.",
                429
            )

        if yanit.status_code >= 500:
            raise YapayZekaServisHatasi(
                "AI-009",
                "Yapay zekâ sağlayıcısında geçici bir sorun var. Lütfen daha sonra deneyin.",
                f"Groq HTTP {yanit.status_code}",
                503
            )

        if not yanit.ok:
            raise YapayZekaServisHatasi(
                "AI-010",
                "Yapay zekâ isteği kabul edilmedi. Model ayarını kontrol edin.",
                f"Groq HTTP {yanit.status_code}: {yanit.text[:500]}",
                503
            )

        try:
            veri = yanit.json()
            cevap = veri["choices"][0]["message"]["content"]

            if not isinstance(cevap, str) or not cevap.strip():
                raise ValueError("Yanıt boş.")

            return cevap.strip()

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            logger.exception("Groq yanıt biçimi beklenenden farklı.")
            raise YapayZekaServisHatasi(
                "AI-011",
                "Yapay zekâdan okunabilir bir yanıt alınamadı. Lütfen tekrar deneyin.",
                f"Yanıt biçimi hatası: {exc}",
                502
            ) from exc

    def _demo_yaniti_ver(self, mesaj):
        """Groq anahtarı yoksa basit demo yanıtları üretir."""

        metin = mesaj.lower()

        if "espresso" in metin:
            oner = (
                "Espresso, yoğun aromalı ve küçük hacimli bir kahvedir. "
                "Sütlü kahvelerin de temelini oluşturur."
            )

        elif any(k in metin for k in (
            "türkiye", "türk kahvesi", "turkish"
        )):
            oner = (
                "Türk kahvesi, ince öğütülmüş kahvenin cezvede "
                "pişirilmesiyle hazırlanır. Köpüğü ve telvesiyle "
                "kendine özgü bir deneyim sunar."
            )

        elif any(k in metin for k in ("kolombiya", "colombia")):
            oner = (
                "Kolombiya kahveleri dengeli gövde ve meyvemsi "
                "veya karamelimsi tatlarla tanınabilir. "
                "Tat profili bölgeye ve işleme yöntemine göre değişir."
            )

        else:
            oner = (
                "Ahenk Coffee'de kahveyi farklı kültürleri "
                "keşfetmenin keyifli bir yolu olarak görüyoruz. "
                "Türk kahvesi, espresso veya filtre kahveyle "
                "keşfe başlayabiliriz."
            )

        return (
            "[DEMO MODU — gerçek yapay zekâ bağlantısı etkin değil]\n\n"
            + oner
            + "\n\nGerçek yapay zekâ yanıtları için geçerli bir "
              "GROQ_API_KEY gereklidir."
        )


yapay_zeka_servisi = AhenkYapayZekaServisi()
