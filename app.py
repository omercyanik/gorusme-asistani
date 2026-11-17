"""Görüşme Asistanı: müşteri danışmanı için görüşme kartı (Streamlit)."""
from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.advisor import SENARYOLAR, durum_notlari, musteri_ozeti, oneriler, senaryo_filtre
from src.data_gen import uret
from src.scripts import AKIS, GENEL_UYUM, ITIRAZLAR

st.set_page_config(page_title="Görüşme Asistanı", layout="wide")


@st.cache_data
def veri_yukle() -> pd.DataFrame:
    return uret(n=1500, seed=42)


def tl(x: int) -> str:
    return f"{x:,} TL".replace(",", ".")


df = veri_yukle()

st.title("Görüşme Asistanı")
st.caption("Sentetik veri, eğitim amaçlı örnek. Gerçek müşteri veya banka verisi yoktur.")

# --- Müşteri seçimi ---
with st.sidebar:
    st.header("Müşteri ara")
    senaryo = st.selectbox("Senaryo", list(SENARYOLAR))
    sorgu = st.text_input("Müşteri no veya ad", placeholder="M100012 ya da Ayşe")
    sonuc = senaryo_filtre(df, senaryo)
    if sorgu:
        s = sorgu.strip().lower()
        sonuc = sonuc[sonuc["musteri_no"].str.lower().str.contains(s) | sonuc["ad_soyad"].str.lower().str.contains(s)]
    if sonuc.empty:
        st.warning("Eşleşen müşteri yok.")
        st.stop()
    secenekler = list(sonuc["musteri_no"].head(50))

    def rastgele_sec() -> None:
        st.session_state["secim"] = random.choice(list(sonuc["musteri_no"]))
        st.session_state["rastgele_ekle"] = True

    st.button("Rastgele müşteri", on_click=rastgele_sec)
    # Rastgele seçilen müşteri ilk 50 dışındaysa listeye ekle
    if st.session_state.pop("rastgele_ekle", False) and st.session_state["secim"] not in secenekler:
        secenekler.insert(0, st.session_state["secim"])
    if st.session_state.get("secim") not in secenekler:
        st.session_state["secim"] = secenekler[0]
    secim = st.selectbox(
        "Sonuçlar",
        secenekler,
        key="secim",
        format_func=lambda no: f"{no} · {df.loc[df.musteri_no == no, 'ad_soyad'].iloc[0]}",
    )
    st.caption(f"{len(sonuc)} kayıt bulundu (ilk 50 gösteriliyor).")

m = df[df["musteri_no"] == secim].iloc[0]

# --- Müşteri 360 ---
st.subheader(f"{m['ad_soyad']} · {m['musteri_no']}")
st.markdown(
    f"**Yaş / Şehir:** {m['yas']} · {m['sehir']}  \n"
    f"**Meslek:** {m['meslek']}  \n"
    f"**Aylık gelir:** {tl(m['aylik_gelir'])}  \n"
    f"**Kredi skoru:** {int(m['kredi_skoru'])}"
)
st.markdown(
    f"**Vadesiz:** {tl(m['vadesiz_bakiye'])} · "
    f"**Vadeli:** {tl(m['vadeli_bakiye'])} · "
    f"**Fon:** {tl(m['fon_bakiye'])}"
)

for k, v in musteri_ozeti(m).items():
    st.write(f"**{k}:** {v}")

for seviye, mesaj in durum_notlari(m):
    (st.warning if seviye == "uyari" else st.info)(mesaj)

tab_oneri, tab_itiraz, tab_akis, tab_uyum, tab_not = st.tabs(
    ["Öneriler", "İtiraz cevapları", "Görüşme akışı", "Uyum listesi", "Görüşme notu"]
)

liste = oneriler(m)

with tab_oneri:
    st.caption("Öneriler müşterinin talebi çözüldükten sonra sunulur. Öncelik puanı 0-100 arasıdır.")
    if not liste:
        st.info("Bu müşteri için öne çıkan öneri yok.")
    for o in liste:
        with st.container(border=True):
            st.markdown(f"#### {o.urun}")
            st.caption(f"Öncelik puanı: {o.puan}/100")
            st.markdown("**Neden:** " + "; ".join(o.gerekce))
            st.markdown(f"**Önerilen açılış:** _{o.acilis}_")
            with st.expander("Bu üründe dikkat edilecekler"):
                for u in o.uyarilar:
                    st.write(f"- {u}")

with tab_itiraz:
    for it in ITIRAZLAR:
        with st.expander(it["baslik"]):
            st.write(it["cevap"])
            st.caption(f"Yaklaşım: {it['teknik']}")

with tab_akis:
    for baslik, aciklama in AKIS:
        st.markdown(f"**{baslik}:** {aciklama}")

with tab_uyum:
    kontrol = [st.checkbox(madde, key=f"uyum_{secim}_{i}") for i, madde in enumerate(GENEL_UYUM)]
    st.caption(f"{sum(kontrol)}/{len(kontrol)} madde tamamlandı")

with tab_not:
    konu = st.text_input("Görüşme konusu", "Genel bilgi talebi")
    sunulan = st.multiselect("Sunulan ürünler", [o.urun for o in liste])
    tepki = st.selectbox("Müşteri tepkisi", ["İlgilendi", "Düşünecek", "Reddetti", "Satış konusu açılmadı"])
    itiraz = st.selectbox("Gelen itiraz", ["Yok"] + [i["baslik"] for i in ITIRAZLAR])
    takip = st.date_input("Takip tarihi", date.today() + timedelta(days=3))
    if st.button("Notu oluştur"):
        not_metni = (
            f"Tarih: {date.today():%d.%m.%Y}\n"
            f"Müşteri: {m['musteri_no']}\n"
            f"Konu: {konu}\n"
            f"Sunulan ürünler: {', '.join(sunulan) or 'Yok'}\n"
            f"Müşteri tepkisi: {tepki}\n"
            f"İtiraz: {itiraz}\n"
            f"Takip tarihi: {takip:%d.%m.%Y}"
        )
        st.code(not_metni, language="text")
