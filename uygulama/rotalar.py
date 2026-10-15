"""Web sayfaları ve JSON API uç noktaları."""
import re
from flask import Blueprint, current_app, jsonify, render_template, request, session, redirect, url_for, flash
from uygulama.database import iletisim_kaydi_ekle, tum_kayitlari_getir
from uygulama.hatalar import DogrulamaHatasi
from uygulama.servisler.yapay_zeka_servisi import yapay_zeka_servisi

import hmac
from uygulama.database import iletisim_kaydi_sil


sayfa_arayuzu = Blueprint("sayfalar", __name__)
api_arayuzu = Blueprint("api", __name__)

@sayfa_arayuzu.get("/")
def ana_sayfa():
    return render_template("index.html")

@sayfa_arayuzu.route("/panel/giris", methods=["GET", "POST"])
def panel_giris():
    if request.method == "POST":
        parola = request.form.get("parola", "")
        beklenen = current_app.config.get("ADMIN_PASSWORD", "")
        if not beklenen:
            flash("Yönetim paneli parolası ayarlanmamış. .env dosyasındaki ADMIN_PASSWORD alanını doldurun.", "error")
        elif parola and parola == beklenen:
            session["panel_giris"] = True
            return redirect(url_for("sayfalar.panel"))
        else:
            flash("Parola doğru değil. Lütfen tekrar deneyin.", "error")
    return render_template("panel_giris.html")

@sayfa_arayuzu.get("/panel/cikis")
def panel_cikis():
    session.pop("panel_giris", None)
    return redirect(url_for("sayfalar.panel_giris"))

@sayfa_arayuzu.get("/panel")
def panel():
    if not session.get("panel_giris"):
        return redirect(url_for("sayfalar.panel_giris"))
    arama = request.args.get("q", "").strip()[:100]
    kayitlar = tum_kayitlari_getir(current_app.config["DATABASE_PATH"], arama)
    return render_template("panel.html", kayitlar=kayitlar, arama=arama, toplam=len(kayitlar))

@sayfa_arayuzu.get("/saglik-durumu")
def saglik_durumu():
    return jsonify({"basari": True, "durum": "çalışıyor", "uygulama": "Ahenk Coffee", "ai_modu": current_app.config.get("AI_PROVIDER", "groq")})

@api_arayuzu.post("/sohbet")
def sohbet_et():
    if not request.is_json:
        raise DogrulamaHatasi("REQ-001", "İstek JSON biçiminde gönderilmelidir.", "Content-Type application/json değil.", 415)
    veri = request.get_json(silent=True)
    if not isinstance(veri, dict):
        raise DogrulamaHatasi("REQ-002", "İstek gövdesi okunamadı. Mesajınızı kontrol edin.", "JSON gövdesi sözlük değil veya bozuk.", 400)
    mesaj = veri.get("mesaj")
    if not isinstance(mesaj, str) or not mesaj.strip():
        raise DogrulamaHatasi("CHAT-001", "Mesaj alanı boş olamaz.", "mesaj alanı eksik veya boş.", 400)
    if len(mesaj) > 2000:
        raise DogrulamaHatasi("CHAT-002", "Mesajınız 2000 karakterden kısa olmalıdır.", f"Mesaj çok uzun: {len(mesaj)} karakter.", 413)
    gecmis = veri.get("gecmis", [])
    if not isinstance(gecmis, list):
        raise DogrulamaHatasi("CHAT-003", "Sohbet geçmişi beklenen biçimde değil. Sayfayı yenileyip tekrar deneyin.", "gecmis list değil.", 400)
    cevap = yapay_zeka_servisi.yanit_uret(mesaj.strip(), gecmis)
    return jsonify({"basari": True, "cevap": cevap})

@api_arayuzu.post("/iletisim")
def iletisim_gonder():
    if not request.is_json:
        raise DogrulamaHatasi("REQ-003", "Form verileri JSON biçiminde gönderilmelidir.", "İletişim isteği JSON değil.", 415)
    veri = request.get_json(silent=True)
    if not isinstance(veri, dict):
        raise DogrulamaHatasi("FORM-001", "Form bilgileri okunamadı. Lütfen tekrar deneyin.", "İletişim JSON gövdesi hatalı.", 400)
    isim = veri.get("isim", "")
    eposta = veri.get("eposta", "")
    ulke = veri.get("ulke", "")
    mesaj = veri.get("mesaj", "")
    izin = veri.get("izin_verildi") is True
    if not all(isinstance(v, str) for v in (isim, eposta, ulke, mesaj)):
        raise DogrulamaHatasi("FORM-002", "Form alanlarının biçimini kontrol edin.", "Form alanlarından biri metin değil.", 400)
    isim, eposta, ulke, mesaj = isim.strip(), eposta.strip(), ulke.strip(), mesaj.strip()
    if not 2 <= len(isim) <= 100:
        raise DogrulamaHatasi("FORM-003", "Adınız 2 ile 100 karakter arasında olmalıdır.", f"Geçersiz isim uzunluğu: {len(isim)}", 400)
    if len(eposta) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", eposta):
        raise DogrulamaHatasi("FORM-004", "Geçerli bir e-posta adresi girin.", "E-posta doğrulaması başarısız.", 400)
    if len(ulke) > 80 or len(mesaj) > 1500:
        raise DogrulamaHatasi("FORM-005", "Ülke alanı en fazla 80, mesaj alanı en fazla 1500 karakter olabilir.", "Form alanı sınırı aşıldı.", 400)
    if not izin:
        raise DogrulamaHatasi("KVKK-001", "İletişim talebiniz için aydınlatma metnini okuyup onay kutusunu işaretleyin.", "Açık rıza/izin kutusu işaretlenmedi.", 400)
    kayit_id = iletisim_kaydi_ekle(current_app.config["DATABASE_PATH"], isim, eposta, ulke, mesaj, izin)
    return jsonify({"basari": True, "mesaj": "Teşekkürler! Ahenk'e bıraktığınız mesaj kaydedildi.", "kayit_id": kayit_id}), 201
