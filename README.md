# Görüşme Asistanı

Canlı demo: https://gorusme-asistani.streamlit.app

Müşteri danışmanı için görüşme kartı. Müşteri numarası girilir; uygulama müşteri özetini, ürün önerilerini,
açılış cümlelerini, itiraz cevaplarını, uyum kontrol listesini ve görüşme notu şablonunu gösterir.

Veriler sentetiktir, gerçek müşteri veya banka verisi içermez. Metinler eğitim amaçlıdır ve gerçek bir bankanın
prosedürü ya da mevzuat yorumu yerine geçmez.

## Neler var
- Müşteri özeti: gelir, skor, bakiyeler, sahip olunan ürünler, son temas, dijital kullanım
- Durum uyarıları: pazarlama izni yok, kayıp riski, düşük skor, dolu kart limiti, yaşlı müşteri
- Kural tabanlı ürün önerileri: gerekçe, 0-100 öncelik puanı, açılış cümlesi ve ürüne özel uyum notları
- İtiraz cevapları, görüşme akışı, uyum kontrol listesi, görüşme notu üretici
- Senaryo filtresi ve rastgele müşteri seçimi

## Kurulum
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Test
```bash
pytest
```

## Yapı
```
app.py            Streamlit arayüzü
src/data_gen.py   Sentetik müşteri verisi (seed ile tekrarlanabilir)
src/advisor.py    Öneri, uyarı ve senaryo kuralları
src/scripts.py    Açılış, itiraz, akış ve uyum metinleri
tests/            Birim testleri
```
