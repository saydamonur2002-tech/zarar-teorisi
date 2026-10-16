# Borç düzeyi ve iç tahvil primi

Çekilme: 2026-10-16. Kurallar: `BORC_PRIM_ONKAYIT.md`. Betik: `borc_prim.py`. Kayıt: `borc_prim_sonuc.json`.

Prim, 10 yıllık gösterge tahvil faizi ile fonlama maliyetinin farkıdır. Tek başına risk primi değildir. Beklenen faiz yolunu ve vade primini de taşır. Denklem kurulmadı. Katsayı yok.

## 1. Üç cümle

H1, H2, H3 ve H4 belirlenemiyor. On yıllık gösterge tahvil faizi ile genel yönetim borç stoku bu çekimde yok. En zayıf halka primin kendisidir: tahvil faizi olmadan fark yazılmaz, borç stoku olmadan düzey de dinamik de yazılmaz.

## 2. Ön kayıt tablosu

Yerel projeksiyon (her ufuk için ayrı denklem; şokun birkaç çeyrek sonraki değerini ölçen yöntem) kilitlendi, uygulanmadı. Eşik 36 çeyrektir. Bant %95’tir.

| Hipotez | Kriter | n | Sonuç | Katsayı | %95 aralık |
| --- | --- | --- | --- | --- | --- |
| H1 düzey, 4 çeyrek | Gecikmeli borç/GSYH, prim düzeyini pozitif etkiler, bant sıfırı dışlar | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı |
| H2 dinamik, 2 çeyrek | Dinamiğin artışı primi pozitif etkiler | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı |
| H3 ters yön, 4 çeyrek | Prim artışı, borç/GSYH değişimini pozitif etkiler | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı |
| H4 beklenti | H1 katsayısı, beklenen faizle en az %50 küçülür | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı |

İşaret değişimi yoktur. İki katsayı da yoktur. Granger çalıştırılmadı.

## 3. Kontrol duyarlılığı

Kontrollü ve kontrolsüz sütun yan yana durmuyor. Kontrol eklenemeden örnek kurulamadı.

| Kontrol | Seri | Durum |
| --- | --- | --- |
| Toplantı öncesi faiz beklentisi | `TP.PKAUO.S04.C.U`, 2025-06…2026-10, n = 17 | Eşiğin altında. Ay sonu beklentisi `TP.PKAUO.S04.A.U` (2013-01…2025-05, n = 149) yerine konmadı |
| VIX | yok | EVDS’de doğrulanmadı. Dış kaynaktan doldurulmadı |
| ABD 10 yıl | yok | EVDS’de doğrulanmadı |
| 24 ay enflasyon beklentisi | `TP.PKAUO.S01.F.U`, 2013-01…2026-10, n = 166 | Duruyor. Tek başına denklem kurmaz |
| USD/TRY | `TP.DK.USD.A.YTL`, 2006-01…2026-10, n = 250 | Duruyor |
| Kırılma kuklaları | 2018, 2020, 2021–22, 2023 | Takvim yazıldı. Örnek olmadığı için tahmin yok |
| Fonlama | `TP.APIFON4`, 2011-01…2026-10, n = 190 | Primin bir ayağı. Tahvil ayağı yok |

## 4. Veri eksikleri

| Eksik | Kapattığı yer |
| --- | --- |
| 10 yıllık gösterge tahvil faizi | Prim, H1, H2, H3, H4 ve dinamiğin faiz ayağı |
| Genel yönetim borç stoku | Borç/GSYH, H1, H2, H3 |
| VIX ve ABD 10 yıl | Kontrollü denklem, zorunlu kontroller durmasa da |
| `TP.PKAUO.S04.C.U`, n = 17 | H1’in beklenti kontrolü ve H4, eşik 36 |

Yakın olup kullanılmayanlar: genel yönetim toplam yükümlülüğü `TP.FINHESTNKS13.ZP45`, 2010-Q4…2026-Q1, n = 50. Borçlanma senedi `TP.FINHESTNKS13.ZP31`, aynı aralık, n = 50. İkisi de borç stoku değildir. GSYH `TP.GSYIH20.BY.B1GQ`, 2006-Q1…2026-Q2, n = 82. Oran yazılmadı.

Çeyreklik ortalama kuralı yazıldı, uygulanmadı. Aylık ara değerleme yapılmadı.

## 5. Monografi

İç tahvil primi (uzun tahvil faizinden merkez bankasının fonlama maliyetini düşünce kalan fark; bu fark hem piyasanın ileride beklediği faizi hem de vadeyi bekletmenin bedelini taşır) bu turda kurulamadı. On yıllık gösterge faiz serisi yok. Genel yönetim borç stokunun gelire oranı da yok. Borç dinamiği (faiz ile gelir büyümesinin farkının borç oranıyla çarpımı) bu iki eksikte yazılmaz. Toplantı öncesi faiz beklentisi on yedi aydır. Otuz altı gözlem eşiğinin altındadır. Sonuç zayıftır: dört hipotez de belirlenemiyor. Eldeki yükümlülük stoku, sorulan borç stoku değildir ve onunla katsayı üretilmedi.

## 6. Eleştiriler

Toplantı öncesi beklenti 2025-06’da başlar ve on yedi aydır. Ondan önceki anket sorusu ay sonu repo beklentisidir ve 2025-05’te biter. İki soru uç uca eklenmedi. Boşluk doldurulmadı. H4’ün istediği kontrol, uzun bir borç örneğiyle aynı ayda durmuyor.

Fonlama maliyeti politika faizinin kendisi değildir. Banka hangi kanaldan fonluyorsa ortalama oraya kayar. Tahvil faizi bu ortalamadan çıkarılınca fark, Hazine’nin ödediği prim ile fonlama bileşiminin kaymasını birlikte taşır. Bir haftalık repo ihale faizi bu çekimde de yoktur. Fark, politika faizine göre kurulmuş bir prim değildir.

Vade primi (uzun vadeyi elde tutmanın, beklenen kısa faiz yolundan ayrı bedeli) bu farkın içinden ayrılmadı. Ayrılacak seri de yoktur. Borç artsa ve fark yükselseydi, bunun ne kadarı “piyasa daha yüksek faiz bekliyor”, ne kadarı “vade bedeli arttı” sorusu açık kalırdı. Bu turda o ayrımın öncesi olan farkın kendisi de yok.
