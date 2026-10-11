"""Uygulamada beklenen hatalar için standart ve anlaşılır hata sınıfları."""
class AhenkHatasi(Exception):
    def __init__(self, kod, kullanici_mesaji, log_mesaji=None, http_durumu=400):
        super().__init__(log_mesaji or kullanici_mesaji)
        self.kod = kod
        self.kullanici_mesaji = kullanici_mesaji
        self.log_mesaji = log_mesaji or kullanici_mesaji
        self.http_durumu = http_durumu

class DogrulamaHatasi(AhenkHatasi):
    pass

class VeritabaniHatasi(AhenkHatasi):
    pass

class YapayZekaServisHatasi(AhenkHatasi):
    pass
