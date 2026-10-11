# Ahenk Coffee — Mimari ve dosya sorumlulukları

## İstek akışı

1. Ziyaretçi `uygulama/sablonlar/index.html` sayfasını açar.
2. Tarayıcıdaki `uygulama/static/js/uygulama.js`, sohbet veya iletişim formu gönderildiğinde JSON isteği yapar.
3. `uygulama/rotalar.py` isteğin biçimini ve alanlarını doğrular.
4. Sohbet isteği `uygulama/servisler/yapay_zeka_servisi.py` katmanına gider; bu katman Groq API'sini çağırır veya anahtar yoksa demo yanıtı verir.
5. İletişim formu `uygulama/database.py` üzerinden SQLite veritabanına kaydedilir.
6. Sonuç tarayıcıya JSON olarak döner; hata varsa hata kodu ve kullanıcıya uygun açıklama gösterilir.

## Katmanların görevleri

| Katman | Dosya | Sorumluluk |
|---|---|---|
| Başlatma | `baslat.py` | Flask uygulamasını oluşturur ve yerel sunucuyu çalıştırır. |
| Yapılandırma | `ayarlar.py`, `.env` | Marka bağlamı, veritabanı yolu, AI modeli ve gizli değerler. |
| Uygulama fabrikası | `uygulama/__init__.py` | Ayarları yükler, veritabanını hazırlar, rotaları kaydeder, ortak hataları yakalar. |
| HTTP katmanı | `uygulama/rotalar.py` | Sayfaları sunar; istek doğrulaması ve yanıt biçimini yönetir. |
| Veri katmanı | `uygulama/database.py` | SQLite bağlantısı, kayıt ekleme ve listeleme. |
| AI servis katmanı | `uygulama/servisler/yapay_zeka_servisi.py` | Groq API bağlantısı, zaman aşımı ve sağlayıcı hataları. |
| Hata sözleşmesi | `uygulama/hatalar.py` | Hata kodu, güvenli kullanıcı mesajı, iç log mesajı ve HTTP durumunu bir arada tutar. |
| Sunum | `uygulama/sablonlar/`, `uygulama/static/` | HTML, CSS ve tarayıcı JavaScript'i. |

## Try/except neden katmanlara ayrıldı?

- **Girdi doğrulaması:** Boş mesaj veya hatalı e-posta gibi beklenen kullanıcı hataları özel hata sınıflarıyla döndürülür; bunlar sunucu çökmesi değildir.
- **Dış servis:** Zaman aşımı, bağlantı hatası, kimlik doğrulama, model bulunamaması ve istek limiti farklı hata kodları alır. Böylece tek bir genel mesaj yerine neyin kontrol edileceği anlaşılır.
- **Veritabanı:** SQLite hatalarında işlem geri alınır (`rollback`) ve bağlantı her koşulda kapatılır (`finally`).
- **Son savunma hattı:** Uygulama fabrikasındaki genel hata yakalayıcı beklenmeyen istisnaları loglar; traceback ve sunucu ayrıntılarını web ziyaretçisine göstermez.

## Tasarım kararları

- SQL sorgularında parametreli ifadeler kullanılır; kullanıcı girdisi sorgu metnine eklenmez.
- Her dosya mümkün olduğunca tek sorumluluk taşır. Örneğin rota dosyası AI API protokolünü veya SQL ayrıntılarını yönetmez.
- Gizli anahtarlar kaynak koduna yazılmaz; `.env.example` yalnızca örnek alanlar içerir.
- Yönetim sayfası oturum kontrolü yapar. Bu temel bir başlangıçtır; canlı kullanımda HTTPS, güvenli çerezler, CSRF koruması, hız sınırlaması ve daha kapsamlı yetkilendirme eklenmelidir.
