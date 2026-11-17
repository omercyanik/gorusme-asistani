"""Kural tabanlı görüşme asistanı: müşteriye göre ürün önerisi ve durum notları."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .scripts import ACILIS, URUN_ADLARI, URUN_UYARILARI

SABIT_GELIRLI_DEGIL = {"Esnaf", "Serbest Meslek", "Öğrenci"}


@dataclass
class Oneri:
    kod: str
    puan: int
    gerekce: list[str] = field(default_factory=list)
    acilis: str = ""
    uyarilar: list[str] = field(default_factory=list)

    @property
    def urun(self) -> str:
        return URUN_ADLARI[self.kod]


def _sinirla(puan: float) -> int:
    return int(max(0, min(100, round(puan))))


def _oneri(kod: str, puan: float, gerekce: list[str], ad: str) -> Oneri:
    return Oneri(
        kod=kod,
        puan=_sinirla(puan),
        gerekce=gerekce,
        acilis=ACILIS[kod].format(ad=ad.split()[0]),
        uyarilar=list(URUN_UYARILARI[kod]),
    )


def durum_notlari(m: pd.Series) -> list[tuple[str, str]]:
    """Görüşme başında danışmanın bilmesi gereken uyarılar: (seviye, mesaj)."""
    notlar: list[tuple[str, str]] = []
    if not m["pazarlama_izni"]:
        notlar.append((
            "uyari",
            "Müşterinin pazarlama/ticari ileti izni yok. Müşteri kendisi sormadıkça aktif satış baskısı yapma; kurum prosedürünü uygula.",
        ))
    if m["son_temas_gun"] > 120 and m["dijital_giris_30g"] == 0:
        notlar.append((
            "bilgi",
            "Uzun süredir temas yok ve dijital giriş yok: önce memnuniyeti sor, satışa sonra geç (kayıp riski).",
        ))
    if m["kredi_skoru"] < 900:
        notlar.append(("uyari", "Kredi skoru düşük: kredi ürünlerinde dikkatli ol, uygunluğu sistemde doğrula."))
    if m["kart_kullanim_orani"] >= 0.9:
        notlar.append(("uyari", "Kart limiti neredeyse dolu: borçlandırıcı ürün önerme."))
    if m["yas"] >= 65:
        notlar.append(("bilgi", "Yaşlı müşteri: sade dil kullan, özet tekrar et, ürünleri acele ettirmeden anlat."))
    return notlar


def oneriler(m: pd.Series, en_fazla: int = 4) -> list[Oneri]:
    """Müşteri için ihtiyaç bağlantılı ürün önerilerini puana göre sıralar."""
    ad = m["ad_soyad"]
    gelir = m["aylik_gelir"]
    skor = m["kredi_skoru"]
    sonuc: list[Oneri] = []

    # Maaş taşıma
    if not m["maas_bizde"] and m["meslek"] not in SABIT_GELIRLI_DEGIL:
        puan = 62 + (10 if gelir >= 40000 else 0) + (6 if m["mobil_aktif"] else 0)
        sonuc.append(_oneri("maas_tasima", puan, [
            f"Meslek: {m['meslek']} (düzenli maaş geliri olası)",
            "Maaş şu an bizde yatmıyor",
        ], ad))

    # Kredi kartı
    if not m["kredi_karti"] and skor >= 1100 and gelir >= 20000:
        puan = 55 + (skor - 1100) / 20 + (5 if m["maas_bizde"] else 0)
        sonuc.append(_oneri("kredi_karti", puan, [
            f"Kartı yok, kredi skoru {skor}",
            f"Aylık gelir {gelir:,} TL".replace(",", "."),
        ], ad))

    # Limit artışı: yüksek kullanım + iyi skor (aşırı doluluk durumunda önerme)
    if m["kredi_karti"] and 0.75 <= m["kart_kullanim_orani"] < 0.9 and skor >= 1400:
        sonuc.append(_oneri("limit_artisi", 58 + (skor - 1400) / 25, [
            f"Kart kullanım oranı %{int(m['kart_kullanim_orani'] * 100)}",
            f"Kredi skoru yüksek ({skor})",
        ], ad))

    # İhtiyaç kredisi
    borc_gelir = m["ihtiyac_kredisi_borc"] / gelir if gelir else 99
    if skor >= 1300 and borc_gelir < 4 and m["meslek"] != "Öğrenci":
        puan = 40 + (skor - 1300) / 15 + (4 - borc_gelir) * 4
        sonuc.append(_oneri("ihtiyac_kredisi", puan, [
            f"Kredi skoru {skor}",
            f"Mevcut ihtiyaç kredisi borcu/gelir oranı {borc_gelir:.1f}",
        ], ad))

    # Vadeli mevduat: atıl vadesiz bakiye
    if m["vadesiz_bakiye"] >= 100_000:
        puan = 55 + min(30, m["vadesiz_bakiye"] / 20_000)
        sonuc.append(_oneri("vadeli_mevduat", puan, [
            f"Vadesiz hesapta {m['vadesiz_bakiye']:,} TL duruyor".replace(",", "."),
        ], ad))

    # Yatırım fonu: toplam birikim yüksek, fon yok
    birikim = m["vadesiz_bakiye"] + m["vadeli_bakiye"]
    if birikim >= 150_000 and m["fon_bakiye"] == 0 and m["yas"] < 65:
        sonuc.append(_oneri("yatirim_fonu", 50 + min(25, birikim / 40_000), [
            f"Toplam birikim {birikim:,} TL, fon bakiyesi yok".replace(",", "."),
            "Risk profili anketi tamamlandıktan sonra konuşulmalı",
        ], ad))

    # BES
    if not m["bes"] and 25 <= m["yas"] <= 55 and gelir >= 30000:
        sonuc.append(_oneri("bes", 48 + min(15, gelir / 8000), [
            f"{m['yas']} yaşında, BES'i yok",
            "Düzenli gelir seviyesi uygun",
        ], ad))

    # Konut sigortası
    if m["konut_kredisi"] and not m["sigorta"]:
        sonuc.append(_oneri("konut_sigortasi", 70, [
            "Konut kredisi var, sigortası görünmüyor",
        ], ad))

    # Mobil bankacılık
    if (not m["mobil_aktif"]) or m["dijital_giris_30g"] <= 1:
        sonuc.append(_oneri("mobil", 52 + (8 if m["yas"] < 45 else 0), [
            "Mobil bankacılık aktif değil ya da çok az kullanılıyor",
            f"Son 30 günde {m['dijital_giris_30g']} dijital giriş",
        ], ad))

    sonuc.sort(key=lambda o: o.puan, reverse=True)
    return sonuc[:en_fazla]


SENARYOLAR = {
    "Tümü": lambda d: d.index == d.index,
    "Maaşı bizde olmayan": lambda d: ~d["maas_bizde"] & ~d["meslek"].isin(SABIT_GELIRLI_DEGIL),
    "Vadesiz bakiyesi yüksek (100 bin TL+)": lambda d: d["vadesiz_bakiye"] >= 100_000,
    "Konut kredisi var, sigortası yok": lambda d: d["konut_kredisi"] & ~d["sigorta"],
    "Kartı yok, skoru yüksek": lambda d: ~d["kredi_karti"] & (d["kredi_skoru"] >= 1400),
    "Kart limiti neredeyse dolu": lambda d: d["kart_kullanim_orani"] >= 0.9,
    "Uzun süredir temas yok (kayıp riski)": lambda d: (d["son_temas_gun"] > 120) & (d["dijital_giris_30g"] == 0),
    "Pazarlama izni yok": lambda d: ~d["pazarlama_izni"],
}


def senaryo_filtre(df: pd.DataFrame, ad: str) -> pd.DataFrame:
    """Seçilen senaryoya uyan müşterileri döndürür."""
    return df[SENARYOLAR[ad](df)]


def musteri_ozeti(m: pd.Series) -> dict[str, str]:
    """Müşteri 360 kartında gösterilecek kısa bilgiler."""
    sahip = [
        ad for ad, var in [
            ("Kredi kartı", m["kredi_karti"]),
            ("Konut kredisi", m["konut_kredisi"]),
            ("BES", m["bes"]),
            ("Sigorta", m["sigorta"]),
            ("Mobil bankacılık", m["mobil_aktif"]),
            ("Maaş hesabı", m["maas_bizde"]),
        ] if var
    ]
    return {
        "Ürünler": ", ".join(sahip) if sahip else "Yalnızca vadesiz hesap",
        "Son temas": f"{m['son_temas_gun']} gün önce",
        "Dijital kullanım": f"Son 30 gün: {m['dijital_giris_30g']} giriş",
    }
