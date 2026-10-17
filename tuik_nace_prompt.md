# PROMPT — TÜİK NACE katmanı

Rol: Titiz veri araştırmacısı. Kuramı doğrulama. Ölç. Yalnız kamuya açık kayıt. Alıntı 15 kelimeyi geçmesin. Uydurma satır yazma. Bulamadığını "bulunamadı, X sorgu denendi" diye yaz. Haber ikincil. Birincil: data.tuik.gov.tr bülten tablosu, TCMB Sektör Bilançoları metaverisi.

Ön kayıt: `cursor/odeme-zinciri-kalicilik-f01a`. 2026-Q1 yoğun silme yüzde 42,1, trilyon TL/ay. NACE bölüm tablosu yok. EVDS istihdam ve sanayi grupları yanlış raftı. Bu tur yalnız TÜİK birincil.

## Alma

- Kurumsal Sektör Hesapları. S.11 ve S.12 haznedir, NACE değildir. NACE sütununa yazılmaz.
- EVDS `bie_rsistihn`, `bie_istihsk4`, `bie_tsny2010`, `bie_tsny2015`, `bie_istihsk3`. Yanlış raf. Tekrar deneme.
- siniflama.tuik.gov.tr. Kod listesidir, gözlem değildir.
- KAP `abcdCode`. NACE değildir.

## Al

1. Faaliyet ağırlığı. Yıllık Sanayi ve Hizmet İstatistikleri, 2024. Bülten: https://data.tuik.gov.tr/Bulten/Index?p=Yillik-Sanayi-ve-Hizmet-Istatistikleri-2024-54051 . Sayfadaki İstatistiksel Tablolar exceli. NACE Rev.2 veya 2.1 kısım. Sütun: girişim, istihdam, ciro, üretim değeri. Kapsam dışı: A, K, O. Dosya adını ve tablo adını yaz.
2. Finansal ağırlık. Sektör Bilançoları, 2024. Bülten: https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080 . İstatistiksel Tablolar exceli. Metaveri: https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Istatistikler/Reel+Sektor+Istatistikleri/Sektor+Bilancolari/ . NACE kısım × aktif, kısa vadeli yabancı kaynak, uzun vadeli yabancı kaynak, özkaynak. Zaman serisi EVDS’de varsa seri kodu yaz. Yoksa bülten exceli yeter.

İkisi ayrı dosya. Biri diğerinin yerine geçmez. Ciro, yabancı kaynak değildir.

## Kod

Çıktı `nace_tuik_agirlik.csv`. Sütun: kaynak (YSHI / sektor_bilanco), yil, nace_kisim, nace_ad, gosterge, deger, pay, dosya_url, tablo_adi.

Pay, aynı kaynak ve aynı gösterge içinde kısımların payıdır. Kapsam dışı kısım paya sokulmaz, "kapsam_disi" diye ayrı satır yazılır.

F haznesinin 2026-Q1 brüt çıkışı yalnız Sektör Bilançoları yabancı kaynak payıyla bölünür. YSHİ ciro payı ikinci sütundur, bölmede kullanılmaz. İki pay yan yana durur. Fark 10 puanı geçerse o kısım "pay_uyumsuz" diye işaretlenir. Ortalama alınmaz.

Her bölüme F'nin silinen oranını yapıştırma. Bölüm bilançosunda iki yönlü kalem ölçülmediyse silinen_oran boş kalır. "Bulunamadı" yaz. Boş hücreyi hazne oranıyla doldurma.

Yıl uyarısı satıra yazılır: "2024 faaliyet veya bilanço ağırlığı, 2026-Q1 akışına uygulandı." Bu varsayımdır. 2026-Q1 NACE gözlemi diye yazılmaz.

## H-N

H-N ancak şu şartta hesaplanır: en az beş NACE kısımda yabancı kaynak payı var ve silinen_oran boş bırakılmış değil, ölçülmüş.

Bu turda silinen_oran ölçülemez. O zaman H-N `test_edilemez` kalır. F yüzde 18,1 ve B yüzde 95,5 H-N sınavı değildir.

H-N açılırsa yanlışlayıcı: kısımlar arası silinen oran farkı 10 puandan küçükse "firma tek tip" düşer. Bir kısım bankaya yakınsa ayrıca yazılır.

## Çıktı

1. Hangi dosya indi, hangi tablo, hangi yıl, hangi NACE sürümü.
2. `nace_tuik_agirlik.csv`.
3. H-N: test_edilemez / hesaplandi. Hesaplandıysa fark ve etiket.
4. Kapsam dışı ve pay_uyumsuz listesi.
5. Arama günlüğü: denenen url, inen dosya adı, boş kalan gösterge.

Yorumu ölçümden ayır. "F haznesi imalattır" deme. "2024 yabancı kaynak payı şöyle" de. Görülmüş yüzdeyi bölüme uydurma.
