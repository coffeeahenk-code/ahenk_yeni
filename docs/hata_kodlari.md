# Ahenk Coffee — Hata kodları ve çözüm adımları

Bu dosya uygulamada gösterilen hata kodlarını açıklar. Kullanıcıya gösterilen metin kısa ve güvenlidir; `loglar/ahenk.log` dosyası geliştiriciye daha fazla teknik ayrıntı verir. Logları paylaşmadan önce e-posta, mesaj veya başka kişisel verileri ayıklayın.

## Sistem ve veritabanı

| Kod | Ne demek? | Kontrol / çözüm |
|---|---|---|
| `LOG-001` | Log dosyası açılamadı. | `loglar` klasörünün yazma izinlerini kontrol edin. Uygulama konsol loglamasıyla devam eder. |
| `DB-001` | Uygulama başlarken veritabanı hazırlanamadı. | `DATABASE_PATH` yolunu, klasör izinlerini ve diskteki boş alanı kontrol edin. |
| `DB-002` | SQLite bağlantısı kurulamadı. | Yolun geçerli olduğunu, klasörün oluşturulabildiğini ve dosyanın erişilebilir olduğunu doğrulayın. |
| `DB-003` | Gerekli tablo oluşturulamadı. | Logdaki SQLite ayrıntısını kontrol edin; dosya izinleri veya bozuk veritabanı söz konusu olabilir. |
| `DB-004` | Kayıt bir veritabanı kısıtına takıldı. | Form alanlarını ve tablo şemasını inceleyin. |
| `DB-005` | Yeni iletişim kaydı yazılamadı. | Disk alanı, yazma izinleri ve SQLite hata ayrıntılarını kontrol edin. İşlem geri alınır. |
| `DB-006` | Yönetim paneli kayıtları okuyamadı. | Veritabanı dosyasına erişimi ve SQLite logunu kontrol edin. |
| `SYS-500` | Beklenmeyen bir uygulama hatası oluştu. | `loglar/ahenk.log` dosyasındaki zaman damgasına karşılık gelen traceback'i inceleyin. İstemciye teknik ayrıntı verilmez. |
| `HTTP-404` | İstenen URL tanımlı değil. | Adres yazımını ve endpoint yolunu kontrol edin. |
| `HTTP-405` | URL var ancak HTTP yöntemi yanlış. | Endpoint'in GET mi POST mu beklediğini kontrol edin. |

## İstek ve form doğrulama

| Kod | Ne demek? | Kontrol / çözüm |
|---|---|---|
| `REQ-001`, `REQ-003` | API isteği JSON olarak gönderilmemiş. | `Content-Type: application/json` başlığı ve istek gövdesini kontrol edin. |
| `REQ-002`, `FORM-001` | JSON okunamadı veya JSON nesne biçiminde değil. | Gövdenin geçerli JSON olduğunu ve nesne içerdiğini doğrulayın. |
| `CHAT-001` | Sohbet mesajı boş. | `mesaj` alanına metin girin. |
| `CHAT-002` | Sohbet mesajı 2000 karakteri geçti. | Soruyu kısaltın. |
| `CHAT-003` | Sohbet geçmişi liste değil. | `gecmis` alanını dizi olarak gönderin; örneğin `[]`. |
| `FORM-002` | Form alanlarından biri metin değil. | `isim`, `eposta`, `ulke` ve `mesaj` alanlarını metin gönderin. |
| `FORM-003` | İsim çok kısa veya uzun. | İsim 2–100 karakter aralığında olmalı. |
| `FORM-004` | E-posta biçimi geçersiz. | `ad@ornek.com` biçiminde geçerli bir e-posta girin. |
| `FORM-005` | Ülke veya mesaj alanı sınırı aştı. | Ülke en fazla 80, mesaj en fazla 1500 karakter olmalı. |
| `KVKK-001` | İzin/onay kutusu işaretlenmemiş. | İlgili aydınlatma metnini okuyup onay kutusunu işaretleyin. Canlı metin hukuk/KVKK gerekliliklerine göre doğrulanmalıdır. |

## Yapay zekâ / Groq bağlantısı

| Kod | Ne demek? | Kontrol / çözüm |
|---|---|---|
| `AI-001` | Desteklenmeyen sağlayıcı seçildi. | Bu sürümde `AI_PROVIDER=groq` kullanılır. |
| `AI-002` | API anahtarı ayarlanmamış; demo yanıtı veriliyor. | `.env` dosyasında `GROQ_API_KEY` alanını doldurun. Demo yanıtı gerçek AI çıktısı değildir. |
| `AI-003` | İstek belirlenen sürede tamamlanmadı. | İnternet bağlantısını kontrol edin; gerekirse `AI_TIMEOUT_SECONDS` değerini artırın. |
| `AI-004` | Groq sunucusuna bağlantı kurulamadı. | İnternet, DNS, güvenlik duvarı ve sağlayıcı durumunu kontrol edin. |
| `AI-005` | Diğer HTTP istemci hatası. | `ahenk.log` dosyasındaki ayrıntıyı inceleyin. |
| `AI-006` | API anahtarı reddedildi (401/403). | Anahtarın doğru olduğunu ve etkin kaldığını doğrulayın. Anahtar sızdıysa iptal edip yenileyin. |
| `AI-007` | Model veya endpoint bulunamadı (404). | `GROQ_MODEL` değerinin hesabınızda erişilebilir olduğundan emin olun; model adları değişebilir. |
| `AI-008` | İstek sınırı aşıldı (429). | Biraz bekleyin ve sağlayıcı kullanım limitlerini kontrol edin. |
| `AI-009` | AI sağlayıcısı 5xx sunucu hatası verdi. | Daha sonra yeniden deneyin ve sağlayıcının servis durumunu kontrol edin. |
| `AI-010` | İstek başka bir HTTP hatasıyla reddedildi. | Model, istek parametreleri ve logdaki HTTP durumunu inceleyin. |
| `AI-011` | Sağlayıcının yanıtı beklenen JSON/metin yapısında değil. | Geçici sağlayıcı sorunu veya API yanıt biçimi değişikliği olabilir. Log ayrıntısını inceleyin. |

## Tarayıcı tarafı kodları

| Kod | Ne demek? | Kontrol / çözüm |
|---|---|---|
| `CHAT-NET-001` | Sohbet isteği sunucuya ulaşamadı veya JSON okunamadı. | Sunucunun çalıştığını, doğru URL'yi ve ağ bağlantısını kontrol edin. |
| `FORM-NET-001` | İletişim formu isteği sunucuya ulaşamadı veya JSON okunamadı. | Sunucuyu, tarayıcı ağ sekmesini ve API yanıtını kontrol edin. |
| `CHAT-CLIENT-001` | Sohbet arayüzü tarafında beklenmeyen hata yakalandı. | Tarayıcı geliştirici araçlarında Console ve Network sekmelerine bakın. |
| `FORM-CLIENT-001` | İletişim arayüzü tarafında beklenmeyen hata yakalandı. | Tarayıcı geliştirici araçlarında Console ve Network sekmelerine bakın. |

## Hata giderme sırası

1. Ekranda görünen hata kodunu not edin.
2. Terminaldeki mesajı ve `loglar/ahenk.log` dosyasının ilgili satırlarını kontrol edin.
3. `.env` dosyasında gizli anahtarların değerini kontrol edin; anahtarın kendisini loglara veya destek mesajlarına kopyalamayın.
4. İlgili çözümü uygulayın ve `/saglik-durumu` adresini kontrol edin.
5. Aynı hatayı tekrar üretip üretmediğini sınayın.
