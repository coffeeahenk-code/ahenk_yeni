"use strict";
const sohbetForm = document.querySelector("#sohbet-form");
if (sohbetForm) {
  const mesajInput = document.querySelector("#mesaj");
  const cikti = document.querySelector("#sohbet-cikti");
  const durum = document.querySelector("#sohbet-durum");
  const gecmis = [];
  sohbetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const mesaj = mesajInput.value.trim();
    if (!mesaj) { durum.textContent = "Lütfen önce bir soru yazın."; return; }
    const dugme = sohbetForm.querySelector("button");
    dugme.disabled = true; durum.textContent = "Kahve rehberi düşünüyor…";
    try {
      const yanit = await fetch("/api/sohbet", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({mesaj, gecmis})});
      let veri;
      try { veri = await yanit.json(); } catch (parseError) { throw new Error("Sunucudan okunabilir bir yanıt alınamadı (JSON_PARSE)."); }
      if (!yanit.ok || !veri.basari) {
        const hata = new Error(veri.hata || "İstek tamamlanamadı."); hata.kod = veri.hata_kodu || `HTTP-${yanit.status}`; throw hata;
      }
      cikti.textContent = veri.cevap;
      gecmis.push({role:"user",content:mesaj},{role:"assistant",content:veri.cevap});
      if (gecmis.length > 10) gecmis.splice(0, gecmis.length - 10);
      mesajInput.value = ""; durum.textContent = "Yanıt hazır.";
    } catch (error) {
      console.error("CHAT-CLIENT-001", error);
      durum.textContent = `${error.kod || "CHAT-NET-001"}: ${error.message || "Bağlantı kurulamadı. Sunucunun çalıştığını kontrol edip tekrar deneyin."}`;
    } finally { dugme.disabled = false; mesajInput.focus(); }
  });
}
const iletisimForm = document.querySelector("#iletisim-form");
if (iletisimForm) {
  const durum = document.querySelector("#form-durum");
  iletisimForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(iletisimForm);
    const veri = {isim:form.get("isim"), eposta:form.get("eposta"), ulke:form.get("ulke") || "", mesaj:form.get("mesaj") || "", izin_verildi:form.get("izin_verildi") === "on"};
    const dugme = iletisimForm.querySelector("button"); dugme.disabled = true; durum.textContent = "Mesajınız gönderiliyor…";
    try {
      const yanit = await fetch("/api/iletisim", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(veri)});
      let sonuc;
      try { sonuc = await yanit.json(); } catch (parseError) { throw new Error("Sunucudan okunabilir yanıt alınamadı (JSON_PARSE)."); }
      if (!yanit.ok || !sonuc.basari) { const hata = new Error(sonuc.hata || "Form gönderilemedi."); hata.kod = sonuc.hata_kodu || `HTTP-${yanit.status}`; throw hata; }
      durum.textContent = sonuc.mesaj; iletisimForm.reset();
    } catch (error) { console.error("FORM-CLIENT-001", error); durum.textContent = `${error.kod || "FORM-NET-001"}: ${error.message || "Bağlantı hatası. Lütfen tekrar deneyin."}`; }
    finally { dugme.disabled = false; }
  });
}
