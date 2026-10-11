# Uluslararası uygulamalar: çok taraflı alacak-borç mahsubu

Soru: "Tek sistem"in (özellikle adım 1: e-fatura alacak-borç döngülerinin nakitsiz mahsubu) ulusal ölçekte uygulandığı ülkeler.
Kaynak: kamuya açık kayıt, 2026-10-11; 12 web sorgusu; kurum raporları, resmî gazeteler, merkez bankası çalışma kâğıdı (HNB W-66), akademik makale (Fleischman–Dini–Littera 2020; Rostowski 1993). Veri: `uluslararasi_uygulamalar.csv` (14 satır).
Kural: hacim yalnız kaynağın yazdığı; "hesap" diye işaretlenen bölme işlemi benim. Bulunamayan "bulunamadı, N sorgu".

## 1. Ulusal, zorunlu, kamu işleticili (adım 1 ile aynı araç)

| Ülke | Sistem / işletici | Yasa | Başlangıç | Zorunluluk | Nesne | Ölçülmüş hacim | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Slovenya | ePobot / AJPES | ZPreZP 2011, ZPreZP-1 | 1991 gönüllü; 15-04-2011 zorunlu | gecikmiş borç ilk aylık tura bildirilir; ihlal vergi idaresine | vadesi geçmiş ihtilafsız borç, fatura | 2025: bildirilen 2.410 mn EUR, mahsup 57,9 mn (%2,4; dikkate alınanın %14,2). 2011 Nis–Ara: 606 mn. 1992: GSYH'nin %7,58'i | `uygulaniyor` |
| Bosna-Hersek / Republika Srpska | MLK / Banja Luka Borsası | Sl. gl. RS 20/14 | 30-10-2015 | yasada evet; yaptırım hiç uygulanmadı | vadesi gelmiş ihtilafsız borç; avans da girilebilir; yılda 6 tur | 10 yıl: 1,52 mlr KM, 53 tur, 2.800+ katılımcı. 2024: 150 mn; 2025: ~214 mn KM. 2015–19 brüt borç azalışı GSYH'nin %8'i. Verim: mahsup edilebilirin %22,6'sı | `uygulaniyor` |
| Romanya | SIC / CPPI Bușteni (Ekonomi Bakanlığı) | OUG 77/1999; HG 773/2019 | 1991-12 tek seferlik; 1999 sürekli | kamu sermayeli şirkete zorunlu (30 gün+); özel gönüllü | kayıtlı ödenmemiş fatura; en çok 12 şirketli devre | 2020-01→2024-05: 10,7 mlr EUR; 381.000 çözüm; ~100 mn EUR/ay; >%90 özel. 1992-01: borcun %75'i (Rostowski) | `uygulaniyor` |
| Çin | 清理三角债 / Devlet Konseyi liderlik grubu, PBoC | 国发〔1990〕19号 | 1990–1992 | idari kampanya | gecikmiş mal bedeli; sabit yatırım projeleri kaynak | 55,5 mlr yuan enjekte (52 banka kredisi) → 219 mlr temizlendi (1:4) | `uygulandi_tarihsel` |
| Rusya, Ukrayna | vzaimozachet / merkez bankaları | MB kararı 1992 | 1992-06/07 | MB işlemi | gecikmiş borç; kalan nete MB kredisi | stok 3,2 trn ruble; 181 mlr ruble kredi; temizlenen bulunamadı (1 sorgu) | `uygulandi_tarihsel` |
| Yugoslavya / FRY | SDK, sonra ZOP | Sl. list SRJ 17/96; 2002 | 1980'ler; 1996–2002 | evet | ihtilafsız borç; kalan için banka kredisi ("dodatna kompenzacija") | bulunamadı (1 sorgu) | `uygulandi_tarihsel` |
| Hırvatistan | ZAP/FINA | doğrulanamadı | ≤2000 | bulunamadı | FINA hesabı anında borç söner | bulunamadı (2 sorgu) | `kismi` |

## 2. Yasa var, gönüllü, özel platform, pilot, reddedilen

| Ülke | Sistem | Tür | Hacim | Durum |
| --- | --- | --- | --- | --- |
| Portekiz | eCompensa (2020-01-01) | yasa + lisanslı özel platform, gönüllü | bulunamadı (1 sorgu) | `yasal_var_hacim_bulunamadi` |
| İspanya | Deudae 2013, Excancel 2014 (%0,9 ücret), Nettit | özel, gönüllü | bulunamadı (1 sorgu) | `ozel_platform` |
| İtalya | Nexyzen (fatura netleştirme); Sardex (karşılıklı kredi, 1 Sardex = 1 EUR) | özel | Sardex 2023: 142 mn; 2014–24 toplam 1 mlr EUR; simülasyon: mahsup tek başına net iç borcu ~%25 | `ozel_platform` |
| İsviçre | WIR Bank (1934) | kooperatif banka, tamamlayıcı para | 2024: >500 mn CHW işlem | `baska_nesne` |
| Karadağ | öneri (2011) | MB Başkanı: etki "ihmal edilecek kadar düşük" | — | `onerildi_uygulanmadi` |
| AB (özel) | Cycles Pay (Informal Systems) | protokol 2025, pilot 2026 | ~20 işletme; simülasyon 1,28 mn fatura | `pilot` |

## 3. Ortak özellikler (ölçüm; tüm `uygulaniyor` satırlarında aynı)

1. **Nesne: vadesi geçmiş, ihtilafsız borç.** Hiçbiri tüm alacak-borç stokunu almaz; gecikmiş ve tartışmasız olanı alır. Bu depodaki F.4 stoku (25.339,8 mlr TL, 2026-Q1) ile taban farklı → `baska_nesne` riski: oranlar stoka uygulanmaz.
2. **Periyodik tur:** Slovenya aylık, RS iki ayda bir, Romanya sürekli çevrimiçi.
3. **Kamu bacağı sistemde:** RS'de hazine %26 + kamu işletmesi %29; Romanya'da kamu sermayeli şirkete zorunlu; Slovenya'da bildirmeyen vergi idaresine şikâyet edilir. Bu depodaki kilitli kapı "ödenmeyen emir" (kamu borcu) üç sistemde açık.
4. **Mahsup oranı küçük:** bildirilenin %2,4'ü (Slovenya 2025); mahsup edilebilirin %22,6'sı (RS); 5 yılda GSYH'nin %8'i (RS). Bu depodaki tavan 0,2582 bu ölçümlerin üstünde kalır; üst sınır olduğu doğrulanır, değer olmadığı da.
5. **Faiz durmaz, ödeme planı yok:** hiçbir sistemde adım 2 ve adım 3 yok. Kalan net borç olağan yolla ödenir.
6. **Kredi enjeksiyonu iki tipe ayırır:** Çin, Rusya, Romanya 1991, FRY → kalan nete banka/MB kredisi (adım 3'ün tersi). Slovenya 2011+, RS, Romanya 1999+ → nakitsiz. Rostowski 1993: kredili tip "tek seferlik" kalmazsa önceki kredi genişlemesini onaylar; Rusya'da 1993 stoku yeniden 15 trn ruble.
7. **Nedensel ölçüm tek:** HNB W-66 (Božić–Zrnc 2022, RS verisi): mahsup 60+ gün geciken firmada hesap bloke olasılığını 22,3 puan düşürür; satışı artırır; yatırımı yalnız nakdi bol firmada artırır. Diğer hacimler kurumların kendi raporu.

## 4. Tek sistemle karşılaştırma (adım adım)

| Adım | Uluslararası karşılık | Eşleşme |
| --- | --- | --- |
| 1 e-fatura mahsup | Slovenya, RS, Romanya (canlı); Çin, Rusya, FRY (tarihsel) | `bulundu`; nesne dar (gecikmiş borç) |
| 2 ödeme planı | bulunamadı; AB 2011/7 ve Sırbistan 60 gün yasası süre sınırı koyar | `bulunamadi` |
| 3 kredisiz, faiz durur | tersi bulundu (kredi enjeksiyonu); faizin durması bulunamadı | `ters_bulundu` |
| 4 endeksli hedef primli senet | aranmadı | `aranmadi` |
| 5 boş stok kira | aranmadı | `aranmadi` |

## 5. Okuma (yorum; ölçüm değil)

- Adım 1 yeni değil: Yugoslavya SDK'dan gelen üç canlı sistem var; en eskisi 35 yıl. Hepsi kamu işleticili ve zorunlu; gönüllü özel platformların (İspanya, Portekiz, Vaysis) hacmi bulunamadı. Bu, Vaysis incelemesindeki "ağ ince" gözlemiyle uyumlu: ağ zorunlulukla yoğunlaşıyor.
- Ölçülen oranlar küçük ve düşüyor (Slovenya 2011 ≈ %6,7 → 2025 %2,4, hesap). Mahsup bir likidite aracı; stok silici değil. "Stok yüzde 20 silindi" cümlesi hiçbir ülkede ölçülmemiş.
- Kredi enjeksiyonu ile çalışan tipler büyük rakam verir (Çin 219 mlr yuan, Romanya %75) ama kalıcılık kaydı zayıf; nakitsiz tipler küçük rakam verir, 10–35 yıl sürer.
- Türkiye'de uygulanacaksa, kayıtta olan şart: gecikmiş-ihtilafsız borç tanımı, aylık tur, kamu borcunun sisteme girmesi, bildirmeyene yaptırım. Bunlar bu depoda kilitli üç kapıdan ikisine (ödenmeyen emir, geçiş payı) denk gelir; seri gelmeden açılmaz.

## Ne denmez

- "Model dünyada uygulanmış" denmez: yalnız adım 1, dar nesneyle.
- "Slovenya'da çalıştı, Türkiye'de de çalışır" denmez: nesne, ölçek, kamu bacağı farklı; Türkiye ölçümü yok.
- "Çin 219 milyar temizledi, mahsup işe yarar" denmez: 52 milyar kredi ile.
- "Yüzde 8 GSYH" Türkiye'ye çevrilmez; RS'nin 5 yıllık kümülatifi.
- Vaysis'in uluslararası emsali İspanyol platformlar; ulusal sistemler değil.
