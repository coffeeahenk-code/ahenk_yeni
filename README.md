# Ahenk Coffee — Python web uygulaması

Bu proje, SmartLead AI Teknik Rehberi'ndeki ayrılmış sorumluluklar yaklaşımı örnek alınarak Ahenk Coffee markasına uyarlanmıştır. Flask tabanlı bir tanıtım sayfası, kahve sohbeti API'si, iletişim formu, SQLite kayıt sistemi ve parola korumalı yönetim paneli içerir.

> **Önemli:** Bu, çalıştırılabilir bir başlangıç projesidir. Canlı işletme kullanımı öncesinde KVKK aydınlatma metni/açık rıza gereklilikleri, HTTPS, yönetici erişim politikası, yedekleme ve güvenlik incelemesi tamamlanmalıdır. Formdaki örnek izin metni hukuki danışmanlık değildir.

## 1. Klasör yapısı

```text
ahenk-coffee/
├── baslat.py                       # Uygulamanın giriş noktası
├── baslat.bat                      # Windows için başlatıcı
├── ayarlar.py                      # Ortam ve marka ayarları
├── gereksinimler.txt               # Python paketleri
├── .env.example                    # Gizli ayarlar için örnek (anahtar içermez)
├── .gitignore                      # .env, veritabanı ve sanal ortamı dışlar
├── README.md
├── veri/                           # SQLite veritabanı burada oluşur
├── loglar/                         # ahenk.log burada oluşur
└── uygulama/
    ├── __init__.py                 # Uygulama fabrikası ve hata yakalayıcılar
    ├── hatalar.py                  # Standart hata sınıfları ve hata kodları
    ├── database.py                 # SQLite işlemleri (Repository katmanı)
    ├── rotalar.py                  # Web sayfaları ve API endpoint'leri
    ├── servisler/
    │   └── yapay_zeka_servisi.py    # Groq bağlantısı ve demo modu
    ├── sablonlar/
    │   ├── index.html
    │   ├── panel_giris.html
    │   └── panel.html
    └── static/
        ├── css/stil.css
        └── js/uygulama.js
```

## 2. Windows'ta kurulum (adım adım)

Terminali açın ve proje klasörüne girin:

```powershell
cd ahenk-coffee
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r gereksinimler.txt
Copy-Item .env.example .env
```

PowerShell, `Activate.ps1` çalıştırmayı engelliyorsa sanal ortamı etkinleştirmek zorunda değilsiniz; yukarıdaki gibi `.venv\Scripts\python.exe` yolunu kullanabilirsiniz.

`.env` dosyasını metin düzenleyicide açın ve en az şu alanları düzenleyin:

```env
FLASK_ORTAMI=gelistirme
SECRET_KEY=uzun-rastgele-bir-gizli-deger
AI_PROVIDER=groq
GROQ_API_KEY=Groq-panelinden-aldiginiz-anahtar
GROQ_MODEL=openai/gpt-oss-120b
ADMIN_PASSWORD=guclu-bir-yonetici-parolasi
```

API anahtarınızı veya gerçek parolanızı kimseyle paylaşmayın; `.env` dosyasını GitHub'a yüklemeyin. `GROQ_MODEL` hesabınızda erişilebilir bir model olmalıdır; model bulunamadı hatası `AI-007` olarak gösterilir. Model isimleri ve erişilebilirlik zamanla değişebilir.

## 3. Uygulamayı çalıştırma

```powershell
.\.venv\Scripts\python.exe baslat.py
```

Tarayıcıda `http://127.0.0.1:5000` adresini açın.

- Ana sayfa: `http://127.0.0.1:5000/`
- Yönetim girişi: `http://127.0.0.1:5000/panel/giris`
- Yönetim paneli: `http://127.0.0.1:5000/panel` (giriş gerekir)
- Sağlık kontrolü: `http://127.0.0.1:5000/saglik-durumu`

`GROQ_API_KEY` boşsa sohbet **demo modunda** çalışır; bu, gerçek AI bağlantısı değildir. API anahtarı girildiğinde sunucu tarafı Groq API'sine bağlanır.

## 4. API sözleşmesi

### `POST /api/sohbet`

İstek JSON örneği:

```json
{"mesaj":"Türk kahvesini özel yapan nedir?","gecmis":[]}
```

Başarılı yanıt: `{"basari": true, "cevap": "..."}`

### `POST /api/iletisim`

```json
{"isim":"Ada Yılmaz","eposta":"ada@example.com","ulke":"Etiyopya","mesaj":"Kahve kültürü hakkında bilgi almak istiyorum.","izin_verildi":true}
```

Başarılı yanıt HTTP 201 döndürür ve `kayit_id` verir. Form doğrulaması sunucuda da yapılır; tarayıcı doğrulaması tek başına güvenlik kontrolü değildir.

## 5. Hata kodları rehberi

| Kod | Anlamı / muhtemel neden | Yapılacak kontrol |
|---|---|---|
| `LOG-001` | Log dosyası oluşturulamadı | `loglar` klasörünün yazma izinlerini kontrol edin; uygulama konsola yazmayı sürdürür. |
| `DB-001` | Başlangıçta DB kurulamadı | `DATABASE_PATH`, klasör yolu ve dosya izinlerini kontrol edin. |
| `DB-002` | SQLite bağlantısı açılamadı | Disk/klasör izinleri, yol ve dosyanın kullanımda olup olmadığını kontrol edin. |
| `DB-003` | Tablo oluşturma hatası | Logdaki SQLite hata ayrıntısını inceleyin; veritabanı dosyasının bozuk/erişilemez olmadığını doğrulayın. |
| `DB-004` | Kayıt kısıt ihlali | Form verilerini ve tablo kısıtlarını kontrol edin. |
| `DB-005` | Yeni kayıt kaydedilemedi | Disk alanını, yazma iznini ve SQLite logunu kontrol edin. |
| `DB-006` | Kayıtlar listelenemedi | Veritabanı dosyasına erişimi ve SQLite hata ayrıntısını kontrol edin. |
| `REQ-001` / `REQ-003` | İstek JSON değil | `Content-Type: application/json` başlığını ve istemci kodunu kontrol edin. |
| `REQ-002` / `FORM-001` | JSON gövdesi okunamadı | İstek gövdesinin geçerli JSON ve nesne olduğunu kontrol edin. |
| `CHAT-001` | Sohbet mesajı boş | `mesaj` alanını doldurun. |
| `CHAT-002` | Sohbet mesajı 2000 karakteri aşıyor | Mesajı kısaltın. |
| `CHAT-003` | Sohbet geçmişi liste değil | `gecmis` alanını dizi olarak gönderin. |
| `FORM-002` | Form alanı metin değil | İsim, e-posta, ülke ve mesaj alanlarını metin gönderin. |
| `FORM-003` | İsim uzunluğu geçersiz | İsim 2–100 karakter olmalı. |
| `FORM-004` | E-posta geçersiz | E-posta adresini kontrol edin. |
| `FORM-005` | Ülke/mesaj sınırı aşıldı | Ülke 80, mesaj 1500 karakteri geçmemeli. |
| `KVKK-001` | İzin kutusu onaylanmadı | Canlıya almadan önce uygun aydınlatma metnini ekleyin; onay olmadan form kaydedilmez. |
| `AI-001` | Desteklenmeyen AI sağlayıcısı | `AI_PROVIDER=groq` olarak ayarlayın. |
| `AI-002` | API anahtarı yok | `.env` içindeki `GROQ_API_KEY` alanını doldurun; aksi durumda demo yanıtı normaldir. |
| `AI-003` | İstek zaman aşımına uğradı | İnternet bağlantısını kontrol edin; gerekirse `AI_TIMEOUT_SECONDS` değerini artırın. |
| `AI-004` | Groq bağlantısı kurulamadı | İnternet, güvenlik duvarı ve Groq servis durumunu kontrol edin. |
| `AI-005` | Diğer HTTP isteği hatası | `ahenk.log` dosyasındaki ayrıntıya bakın. |
| `AI-006` | API anahtarı yetkisiz/yanlış | Groq anahtarını kontrol edin; sızdıysa iptal edip yenisini oluşturun. |
| `AI-007` | Model/endpoint bulunamadı (404) | `GROQ_MODEL` değerinin Groq hesabınızda erişilebilir olduğunu doğrulayın. |
| `AI-008` | İstek sınırı aşıldı (429) | Biraz bekleyin, kullanım limitlerini kontrol edin. |
| `AI-009` | AI sağlayıcısı 5xx döndürdü | Daha sonra tekrar deneyin ve servis durumunu kontrol edin. |
| `AI-010` | AI isteği başka nedenle reddedildi | Model, istek parametreleri ve logdaki HTTP durumunu inceleyin. |
| `AI-011` | AI yanıt biçimi beklenenden farklı | Model/API yanıtını kontrol edin; sağlayıcı geçici sorun yaşıyor olabilir. |
| `HTTP-404` | Adres bulunamadı | URL ve endpoint yolunu kontrol edin. |
| `HTTP-405` | Yanlış HTTP yöntemi | Endpoint'in GET/POST beklentisini kontrol edin. |
| `SYS-500` | Beklenmeyen hata | `loglar/ahenk.log` dosyasını inceleyin; kullanıcıya traceback gösterilmez. |
| `CHAT-NET-001` / `FORM-NET-001` | Tarayıcı sunucuya ulaşamıyor | Python sunucusunun çalıştığını, adresi ve ağ bağlantısını kontrol edin. |
| `CHAT-CLIENT-001` / `FORM-CLIENT-001` | Tarayıcı tarafında işlem hatası | Geliştirici araçlarının Console bölümüne ve ekrandaki hata koduna bakın. |

### Try/except yaklaşımı

- Beklenen hatalar kendi sınıflarıyla (`DogrulamaHatasi`, `VeritabaniHatasi`, `YapayZekaServisHatasi`) yakalanır ve uygun HTTP koduyla döndürülür.
- Ağ isteklerinde zaman aşımı, bağlantı hatası ve HTTP yanıtları ayrı ayrı ele alınır.
- Veritabanı yazımı başarısızsa `rollback()` yapılır ve bağlantı `finally` içinde kapatılır.
- En son genel hata yakalayıcı beklenmeyen hataları loglar; özel sistem ayrıntılarını ziyaretçiye açmaz.
- Hataları sessizce yutmak yerine açıklayıcı hata kodu, log mesajı ve kullanıcıya uygun bir metin üretilir.

## 6. Güvenlik ve canlıya alma notları

1. `.env` dosyasını ve gerçek API anahtarlarını depoya yüklemeyin.
2. Canlı ortamda `FLASK_ORTAMI=uretim` kullanın; debug açık kalmamalıdır.
3. `SECRET_KEY` ve `ADMIN_PASSWORD` değerlerini güçlü, benzersiz değerlerle değiştirin.
4. SQLite dosyasını herkese açık statik klasörlere koymayın; bu projede `veri/` altındadır.
5. Yönetim paneli temel parola oturumu kullanır; üretim ortamında HTTPS, güvenli çerez ayarları, hız sınırlama ve daha güçlü erişim kontrolü ekleyin.
6. Bu başlangıç sürümünde CSRF koruması ve otomatik veri saklama/silme politikası eklenmemiştir. Canlı kullanımdan önce bunları uygulayın.
7. CORS bu sürümde ayrıca açılmamıştır; aynı origin'den çalışan arayüz için gerekmez. Wix gibi farklı bir origin'den bağlanacaksanız yalnızca izin verilen domainleri kapsayan kontrollü CORS yapılandırması ekleyin.
8. İletişim verileri kişisel veri olabilir. Form metni, saklama süresi ve erişim politikası canlıya almadan önce gözden geçirilmelidir.

## 7. Render gibi bir serviste yayınlama

Bu proje için örnek komutlar:

- Build Command: `pip install -r gereksinimler.txt`
- Start Command: `gunicorn baslat:uygulama`
- Environment Variables: `FLASK_ORTAMI=uretim`, `SECRET_KEY`, `ADMIN_PASSWORD`, gerekiyorsa `GROQ_API_KEY`, `GROQ_MODEL`

SQLite dosyası bazı bulut servislerinde yeniden dağıtımda kalıcı olmayabilir. Kalıcı disk veya yönetilen veritabanı yapılandırmasını doğrulamadan gerçek müşteri kayıtları için kullanmayın.
#   a h e n k _ y e n i  
 "# ahenk_yeni" 
#   a h e n k _ y e n i  
 #   a h e n k _ y e n i  
 #   a h e n k _ y e n i  
 