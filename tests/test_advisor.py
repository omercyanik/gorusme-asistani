import pandas as pd

from src.advisor import durum_notlari, oneriler
from src.data_gen import uret


def musteri(**ek) -> pd.Series:
    temel = dict(
        musteri_no="M1", ad_soyad="Ayşe Kaya", yas=35, sehir="Ankara", meslek="Öğretmen",
        aylik_gelir=40000, kredi_skoru=1400, maas_bizde=False, vadesiz_bakiye=10000,
        vadeli_bakiye=0, fon_bakiye=0, kredi_karti=False, kart_limit=0,
        kart_kullanim_orani=0.0, ihtiyac_kredisi_borc=0, konut_kredisi=False, bes=False,
        sigorta=False, mobil_aktif=True, dijital_giris_30g=10, son_temas_gun=10,
        pazarlama_izni=True,
    )
    temel.update(ek)
    return pd.Series(temel)


def kodlar(m):
    return [o.kod for o in oneriler(m, en_fazla=20)]


def test_veri_deterministik():
    assert uret(50, seed=1).equals(uret(50, seed=1))


def test_veri_sekli_ve_benzersiz_no():
    df = uret(200, seed=3)
    assert len(df) == 200
    assert df["musteri_no"].is_unique
    assert df["kredi_skoru"].between(200, 1900).all()


def test_maas_tasima_onerilir():
    assert "maas_tasima" in kodlar(musteri())


def test_maas_bizdeyse_onerilmez():
    assert "maas_tasima" not in kodlar(musteri(maas_bizde=True))


def test_serbest_meslege_maas_tasima_yok():
    assert "maas_tasima" not in kodlar(musteri(meslek="Serbest Meslek"))


def test_dusuk_skora_kredi_yok():
    k = kodlar(musteri(kredi_skoru=800))
    assert "ihtiyac_kredisi" not in k and "kredi_karti" not in k


def test_limit_dolu_kartta_artis_onerilmez():
    m = musteri(kredi_karti=True, kart_limit=50000, kart_kullanim_orani=0.95, kredi_skoru=1700)
    assert "limit_artisi" not in kodlar(m)
    assert any(s == "uyari" for s, _ in durum_notlari(m))


def test_konut_sigortasi():
    assert "konut_sigortasi" in kodlar(musteri(konut_kredisi=True))


def test_yatirim_fonu_ve_uyari():
    m = musteri(vadesiz_bakiye=300000)
    fon = [o for o in oneriler(m, 20) if o.kod == "yatirim_fonu"][0]
    assert any("risk profili" in u.lower() or "uygunluk" in u.lower() for u in fon.uyarilar)


def test_pazarlama_izni_uyarisi():
    assert any("izni yok" in msg for _, msg in durum_notlari(musteri(pazarlama_izni=False)))


def test_sirali_ve_sinirli():
    liste = oneriler(musteri(vadesiz_bakiye=400000, mobil_aktif=False), en_fazla=3)
    assert len(liste) <= 3
    assert [o.puan for o in liste] == sorted([o.puan for o in liste], reverse=True)
    assert all(0 <= o.puan <= 100 for o in liste)


def test_tum_veri_hatasiz_calisir():
    df = uret(300, seed=7)
    for _, m in df.iterrows():
        oneriler(m)
        durum_notlari(m)


def test_senaryolar_bos_degil_ve_dogru_filtreler():
    from src.advisor import SENARYOLAR, senaryo_filtre

    df = uret(1500, seed=42)
    for ad in SENARYOLAR:
        assert len(senaryo_filtre(df, ad)) > 0, ad
    assert len(senaryo_filtre(df, "Tümü")) == len(df)
    assert senaryo_filtre(df, "Konut kredisi var, sigortası yok")["sigorta"].eq(False).all()
    assert senaryo_filtre(df, "Pazarlama izni yok")["pazarlama_izni"].eq(False).all()
