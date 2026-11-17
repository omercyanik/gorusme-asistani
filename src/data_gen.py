"""Sentetik müşteri verisi üretici.

Tüm kayıtlar rastgele üretilir; gerçek kişi, hesap veya kurum verisi içermez.
Aynı seed her zaman aynı veri setini üretir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ADLAR = [
    "Ahmet", "Mehmet", "Ayşe", "Fatma", "Mustafa", "Emine", "Ali", "Hatice",
    "Hüseyin", "Zeynep", "Hasan", "Elif", "İbrahim", "Merve", "Yusuf", "Büşra",
    "Murat", "Selin", "Emre", "Derya", "Can", "Esra", "Burak", "Gamze",
    "Kerem", "Nur", "Cem", "Sevgi", "Onur", "Pınar",
]
SOYADLAR = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk",
    "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara",
    "Koç", "Kurt", "Özkan", "Şimşek", "Polat", "Korkmaz", "Erdoğan", "Güneş",
]
SEHIRLER = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Kocaeli", "Konya",
    "Adana", "Gaziantep", "Trabzon", "Samsun", "Eskişehir",
]
# meslek: (ortalama aylık gelir, maaş hesabı bankaya taşınabilir mi)
MESLEKLER = {
    "Öğretmen": (38000, True),
    "Mühendis": (65000, True),
    "Sağlık Çalışanı": (55000, True),
    "Memur": (42000, True),
    "Özel Sektör Çalışanı": (45000, True),
    "Emekli": (22000, True),
    "Esnaf": (50000, False),
    "Serbest Meslek": (70000, False),
    "Öğrenci": (9000, False),
}


def uret(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """n adet sentetik bireysel müşteri üretir."""
    rng = np.random.default_rng(seed)
    meslekler = list(MESLEKLER)
    meslek = rng.choice(meslekler, size=n, p=[0.09, 0.10, 0.09, 0.10, 0.28, 0.12, 0.08, 0.07, 0.07])

    ort_gelir = np.array([MESLEKLER[m][0] for m in meslek], dtype=float)
    gelir = np.round(ort_gelir * rng.lognormal(0, 0.28, n), -2)

    yas = np.where(
        meslek == "Emekli", rng.integers(58, 80, n),
        np.where(meslek == "Öğrenci", rng.integers(18, 26, n), rng.integers(23, 62, n)),
    )

    skor = np.clip(rng.normal(1250, 320, n), 200, 1900).round().astype(int)

    # Ürün sahipliği: gelir ve skor yükseldikçe olasılık artar
    gelir_z = (gelir - gelir.mean()) / gelir.std()
    skor_z = (skor - skor.mean()) / skor.std()

    def bayrak(taban: float, gelir_etkisi: float = 0.0, skor_etkisi: float = 0.0) -> np.ndarray:
        p = np.clip(taban + gelir_etkisi * gelir_z + skor_etkisi * skor_z, 0.02, 0.97)
        return rng.random(n) < p

    maas_bizde = np.array([MESLEKLER[m][1] for m in meslek]) & (rng.random(n) < 0.45)
    kredi_karti = bayrak(0.62, 0.08, 0.10)
    kart_limit = np.where(kredi_karti, np.round(gelir * rng.uniform(1.0, 3.5, n), -3), 0)
    kart_kullanim = np.where(kredi_karti, np.clip(rng.beta(2, 3, n), 0, 1), 0).round(2)
    konut_kredisi = bayrak(0.10, 0.06, 0.04) & (yas > 28)
    bes = bayrak(0.18, 0.05, 0.02) & (yas < 65)
    sigorta = bayrak(0.15, 0.05, 0.02) | (konut_kredisi & (rng.random(n) < 0.5))
    mobil_aktif = rng.random(n) < np.clip(0.9 - (yas - 25) * 0.008, 0.35, 0.95)
    dijital_giris = np.where(mobil_aktif, rng.poisson(9, n), rng.poisson(0.4, n))

    vadesiz = np.round(gelir * rng.exponential(1.6, n), -2)
    vadeli = np.where(bayrak(0.18, 0.08, 0.02), np.round(gelir * rng.exponential(2.5, n), -3), 0)
    fon = np.where(bayrak(0.08, 0.07, 0.02), np.round(gelir * rng.exponential(2.0, n), -3), 0)
    ihtiyac_borc = np.where(bayrak(0.22, -0.02, -0.05), np.round(gelir * rng.uniform(1.0, 8.0, n), -3), 0)

    son_temas = np.minimum(rng.exponential(55, n), 400).astype(int)

    df = pd.DataFrame(
        {
            "musteri_no": [f"M{100000 + i}" for i in range(n)],
            "ad_soyad": [f"{rng.choice(ADLAR)} {rng.choice(SOYADLAR)}" for _ in range(n)],
            "yas": yas,
            "sehir": rng.choice(SEHIRLER, size=n),
            "meslek": meslek,
            "aylik_gelir": gelir.astype(int),
            "kredi_skoru": skor,
            "maas_bizde": maas_bizde,
            "vadesiz_bakiye": vadesiz.astype(int),
            "vadeli_bakiye": vadeli.astype(int),
            "fon_bakiye": fon.astype(int),
            "kredi_karti": kredi_karti,
            "kart_limit": kart_limit.astype(int),
            "kart_kullanim_orani": kart_kullanim,
            "ihtiyac_kredisi_borc": ihtiyac_borc.astype(int),
            "konut_kredisi": konut_kredisi,
            "bes": bes,
            "sigorta": sigorta,
            "mobil_aktif": mobil_aktif,
            "dijital_giris_30g": dijital_giris.astype(int),
            "son_temas_gun": son_temas,
            "pazarlama_izni": rng.random(n) < 0.72,
        }
    )
    return df


if __name__ == "__main__":
    veri = uret()
    print(veri.head())
    print(veri.shape)
