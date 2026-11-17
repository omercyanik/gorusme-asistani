"""Görüşme içerikleri: akış, açılış cümleleri, itiraz cevapları, uyum listeleri.

Metinler eğitim amaçlı örneklerdir. Gerçek bir bankanın prosedürü, ürün koşulları
veya mevzuat yorumu yerine geçmez; kullanmadan önce kurum prosedürüyle doğrulanmalıdır.
"""
from __future__ import annotations

AKIS = [
    ("1. Karşılama", "Kendini ve kurumu tanıt, müşteriye adıyla hitap et."),
    ("2. Kimlik doğrulama", "Kurum prosedüründeki doğrulama adımlarını tamamla. Doğrulama olmadan hesap bilgisi paylaşma."),
    ("3. İhtiyaç tespiti", "Önce dinle: müşterinin talebi ne? Açık uçlu 1-2 soru sor (ör. 'Bu ay en çok neyi kolaylaştırmak isterdiniz?')."),
    ("4. Çözüm / öneri", "Talebi çöz. Ardından ihtiyaçla bağlantılı en fazla 1-2 öneri sun; müşterinin talebi çözülmeden satışa geçme."),
    ("5. İtiraz yönetimi", "Dinle, empati kur, sorusunu yanıtla; baskı yapma."),
    ("6. Bilgilendirme ve onay", "Ürün koşulları, maliyet ve yükümlülükleri açıkça anlat; müşterinin onayını al."),
    ("7. Kapanış ve not", "Yapılanları özetle, takip tarihini söyle, görüşme notunu sisteme gir."),
]

URUN_ADLARI = {
    "maas_tasima": "Maaş taşıma",
    "kredi_karti": "Kredi kartı",
    "limit_artisi": "Kart limit artışı",
    "ihtiyac_kredisi": "İhtiyaç kredisi",
    "vadeli_mevduat": "Vadeli mevduat",
    "yatirim_fonu": "Yatırım fonu",
    "bes": "Bireysel emeklilik (BES)",
    "konut_sigortasi": "Konut / kredi hayat sigortası",
    "mobil": "Mobil bankacılık",
}

ACILIS = {
    "maas_tasima": "{ad} Bey/Hanım, maaşınızı bizde alırsanız hesabınızda maaşa özel avantajları da kullanabilirsiniz. Şu an maaşınızı hangi bankadan alıyorsunuz, memnun musunuz?",
    "kredi_karti": "Hesabınızı incelerken kartınızın olmadığını gördüm. Günlük harcamalarınızı nasıl yapıyorsunuz, kart sizin için işe yarar mı?",
    "limit_artisi": "Kartınızı düzenli kullandığınızı görüyorum. Son dönemde limit yetersiz kaldığı oldu mu?",
    "ihtiyac_kredisi": "Önümüzdeki dönemde planladığınız bir harcama var mı? Varsa size uygun seçenekleri birlikte inceleyebiliriz.",
    "vadeli_mevduat": "Hesabınızda bir süredir bekleyen tutar var. Bu parayı kısa vadede kullanmayı düşünüyor musunuz, yoksa değerlendirmek ister misiniz?",
    "yatirim_fonu": "Birikimlerinizi değerlendirmek konusunda bir planınız var mı? Önce risk tercihinizi öğrenmek isterim.",
    "bes": "Uzun vadeli birikim yapmayı düşündünüz mü? BES'in nasıl çalıştığını ve şartlarını kısaca anlatabilirim.",
    "konut_sigortasi": "Konut krediniz için sigorta durumunuzu birlikte kontrol edelim mi?",
    "mobil": "Mobil bankacılığı henüz çok kullanmadığınızı görüyorum. Havale ve fatura işlemleri için size kısaca gösterebilirim.",
}

# Ürüne özel uyum maddeleri (genel hatırlatmalar; kurum prosedürü esastır)
URUN_UYARILARI = {
    "maas_tasima": ["Müşteri kararını kendisi vermeli; baskı veya yanıltıcı vaat yok."],
    "kredi_karti": ["Faiz, aidat ve diğer ücretleri açıkça söyle.", "Müşterinin ödeme gücüne uygun limit konuş."],
    "limit_artisi": ["Borçluluk durumunu kontrol et.", "Yüksek kullanım oranında dikkatli ol; müşteriyi borçlandırma baskısı yok."],
    "ihtiyac_kredisi": ["Faiz, toplam geri ödeme tutarı ve masrafları anlat.", "Borç/gelir oranını kontrol et.", "Müşteri için gerçekten ihtiyaç olup olmadığını sor."],
    "vadeli_mevduat": ["Vade bitmeden bozma durumunu ve faiz koşullarını anlat."],
    "yatirim_fonu": ["Yatırım ürünleri için uygunluk/risk profili anketi tamamlanmalı.", "Getiri garantisi verme; geçmiş getiri geleceği garanti etmez."],
    "bes": ["Devlet katkısı ve ayrılma koşullarını güncel mevzuattan doğrulayarak anlat.", "Ürün risk ve kesintilerini açıkla."],
    "konut_sigortasi": ["Teminat kapsamını ve istisnaları açıkla.", "Zorunlu/isteğe bağlı ayrımını doğru yap."],
    "mobil": ["Şifre, SMS kodu ve güvenlik bilgilerini hiçbir zaman isteme ve paylaştırma."],
}

GENEL_UYUM = [
    "Kimlik doğrulama prosedürü tamamlandı.",
    "Müşterinin talebi çözüldü, ardından öneri yapıldı.",
    "Ürün koşulları ve maliyetler açıkça anlatıldı.",
    "Müşteri onayı alındı; baskı veya yanıltıcı ifade kullanılmadı.",
    "Kişisel veriler yalnızca gerekli ölçüde kullanıldı (KVKK).",
    "Görüşme notu sisteme girildi.",
]

ITIRAZLAR = [
    {
        "baslik": "Faiz / ücret yüksek",
        "cevap": "Haklısınız, maliyet önemli. Size toplam ödeyeceğiniz tutarı ve masrafları açıkça göstereyim; uygun gelmezse başka vade veya tutar seçeneklerini de karşılaştıralım.",
        "teknik": "Empati + şeffaflık",
    },
    {
        "baslik": "Düşüneyim",
        "cevap": "Tabii, acele etmeyin. Karar vermenizi en çok neyin zorlaştırdığını öğrenebilir miyim? Size bilgileri yazılı gönderip yarın/hafta sonu tekrar arayabilirim; uygun mudur?",
        "teknik": "Gerekçeyi öğren + takip tarihi al",
    },
    {
        "baslik": "Başka bankada daha iyisi var",
        "cevap": "Karşılaştırma yapmanız çok doğru. Hangi koşulu daha avantajlı buldunuz? Biz de hangi konularda farkımızı sunabiliriz birlikte bakalım; uygun değilse sizi yönlendirmem.",
        "teknik": "Merak + dürüstlük",
    },
    {
        "baslik": "İhtiyacım yok",
        "cevap": "Anladım, ihtiyacınız yoksa bunu zorlamak istemem. İleride lazım olursa bilgi verebilmem için size ürünle ilgili kısa bir not bırakabilirim.",
        "teknik": "Saygı göster, kapıyı açık bırak",
    },
    {
        "baslik": "Güvenmiyorum / dijitali kullanmam",
        "cevap": "Güvenlik konusunda çekincenizi anlıyorum. Bankamız SMS kodunu asla telefonda istemez; isterseniz hesabınızı güvenli hale getirmek için nelere dikkat edeceğinizi anlatayım.",
        "teknik": "Güvenlik odaklı eğitim",
    },
    {
        "baslik": "Şu an param yok / bütçem dar",
        "cevap": "Durumunuzu anlıyorum. Bütçenize yük olacak bir ürünü önermem; öncelikli olarak mevcut ödemelerinizi rahatlatacak seçeneklere bakmak ister misiniz?",
        "teknik": "Müşterinin yararını öne al",
    },
]
