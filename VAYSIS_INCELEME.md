# Vaysis incelemesi

Kaynak: kamuya açık kayıt, 2026-10-11. vaysis.com (ana sayfa, KVKK sayfası, istemci JS paketi `assets/index-D0QH9EsT.js` 2,6 MB), PitchBook profili, bouncewatch profili, Wayback Machine (4 arşiv), RDAP alan adı kaydı, 3 web sorgusu. Şirketle görüşülmedi. Kurucu adı bulunamadı (2 sorgu). Alıntılar 15 kelimeyi geçmez; niyet atfedilmez.

## 1. Kimlik ve durum

| Alan | Kayıt | Kaynak |
| --- | --- | --- |
| Kuruluş | 2019 | PitchBook, bouncewatch |
| Yer | İstanbul, Kadıköy (Koşuyolu, Mehmet Akfan Sk. 23) | PitchBook |
| Çalışan | 2–10 | bouncewatch |
| Hızlandırıcı | 07-10-2020, "Accelerator/Incubator"; program adı yok | PitchBook |
| Durum | "Out of Business", 29-07-2025 | PitchBook |
| Site | Canlı, "© 2026 VAYSIS"; "Geliştirme: Lovable · Yayınlama: Natro" | vaysis.com |
| Alan adı | vaysis.com kaydı 11-11-2014; son değişiklik 25-03-2026; yazmaç Nics Telekomünikasyon; NS Natro | RDAP (Verisign) |
| Wayback | 4 kayıt: 2020-10-13, 2021-04-20, 2026-05-12, 2026-06-18; 2021-05 → 2026-04 arası kayıt yok | archive.org |
| Eski ad | "Vadeli Alacak Yönlendirme Sistemi" | bouncewatch |
| Yeni ad | "Valörlü Alacak Yönetim Sistemi" | vaysis.com |
| Kurucu | bulunamadı | 2 sorgu |

Çelişki: PitchBook 2025'te faaliyet dışı yazar; site 2026'da canlı ve yeniden yapılmış (Lovable, yapay zekâ ile uygulama üreten araç). İkisi de kayıt; hangisinin güncel olduğu bu kaynaklarla belirlenemedi. Faaliyet hacmi, üye sayısı, mahsup tutarı hiçbir kaynakta yok.

### 1a. Ne zaman açılmış (zaman çizgisi; kayıt tarihleri)

| Tarih | Kayıt | Kaynak |
| --- | --- | --- |
| 2014-11-11 | vaysis.com alan adı alındı | RDAP |
| 2019 | şirket kuruluşu | PitchBook, bouncewatch |
| 2020-10-07 | hızlandırıcı/kuluçka kaydı | PitchBook |
| 2020-10-13 | ilk site arşivi: başlık "Vaysis / Vadeli Alacak Yönlendirme Sistemi"; Vue uygulaması, Google Analytics kimliği var; içerik JS'siz görünmez | Wayback |
| 2021-04-20 | ikinci arşiv: başlık "Vaysis"; `vaysis-frontend` Vue uygulaması; JS dosyaları arşivde yok (404) | Wayback |
| 2021-05 → 2026-04 | arşiv yok | Wayback |
| 2025-07-29 | "Out of Business" kaydı | PitchBook |
| 2026-03-25 | alan adı kaydında son değişiklik | RDAP |
| 2026-05-12 | üçüncü arşiv: başlık "Lovable App", açıklama "Lovable Generated Project"; şablon, içerik girilmemiş | Wayback |
| 2026-06-18 | dördüncü arşiv: "VAYSIS — Alacak Yönlendirme Platformu"; paket `index-D0QH9EsT.js` / `index-CKYaPJ6D.css`; derleme kimliği `8675a573` | Wayback |
| 2026-06-18 → 2026-10-11 | ara arşiv yok | Wayback |
| 2026-10-11 | bugün: aynı paket, aynı derleme kimliği `8675a573`; yalnız Lovable izleme betiği değişmiş. "Valörlü Alacak Yönetim Sistemi", fiyat, KYC, token, e-imza akışı bu pakette | vaysis.com |

Bugünkü içerik en geç 2026-06-18'de yayındaydı (aynı JS/CSS adı ve derleme kimliği); o tarihten bu yana kod değişmemiş. "İki ay önce açıldı" (2026-08) kayıtla desteklenmez; bugünkü sürüm ≥ 4 ay önce yayında. İlk yayın tarihi 2026-05-12 (boş şablon) ile 2026-06-18 arasında; gün bilinmiyor.

Okuma (yorum): İlk açılış 2020 (site) / 2019 (şirket). 2026'da açılan, **yeniden yapılmış site**: 2026-05'te boş Lovable şablonu, 2026-06'da ad, 2026-10'da bugünkü içerik. 2020–2021 sitesinde ne vardı bilinmiyor (JS arşivlenmemiş). Yani "2026'da açıldı" doğru değil; "2026'da yeniden açıldı / yeniden yazıldı" kayıtla uyumlu. 2021-05 ile 2026-04 arası boşluk faaliyet yokluğu demek değil; arşivleme olmaması demek.

## 2. Mekanizma (sitenin yazdığı)

1. Üyelik: e-posta + VKN; KYC (e-Devlet ile T.C. kimlik doğrulama, 5 dakikalık video görüşme, ya da "demo doğrulama").
2. Alacak tanımı: fatura yükleme veya ERP aktarımı (Starvay entegrasyonu; "ERP'den aktarılan faturalar otomatik alacağa dönüşür").
3. "Tokenize": onaylı alacak "dijital token olarak takas merkezine kaydedilir; izlenebilir, bölünebilir ve devredilebilir".
4. Mahsup: "Valör ve tutar olarak uyumlu alacaklar listeleniyor"; eşleşme → devir sözleşmesi; iki taraf nitelikli e-imza (Turkcell mobil imza) ile imzalar; "Her iki taraf da sözleşmeyi imzaladı. Devir işlemi onaylandı."
5. Alternatif kanal: alacağı vade öncesi başka üyeye satma veya "Fatura Pazarı"nda satış (nakit; alacak satışı, mahsup değil).
6. Ücret: üyelik 12 USD/ay; işlem ‰1–3 ("Devir işlemlerinde uygulanan orantısal hizmet bedeli"); ödeme "USD kontör" ile; "Başarısız işlemde ücret yok."

Hukuki araç: Türk Borçlar Kanunu temliki (alacağın devri) + e-imza. Yani çok taraflı mahsup, ikili devir sözleşmeleri zinciriyle kurulur; merkezi karşı taraf yok.

## 3. Kod izleri (yalnız istemci paketi; sunucu görülmedi)

- Veri tabloları (Supabase): `vaysis_companies`, `vaysis_receivables`, `vaysis_transfers`, `vaysis_signatures`, `vaysis_credits`, `vaysis_credit_purchases`, `vaysis_credit_transactions`, `vaysis_external_payments`, `vaysis_service_fee_tiers`, `vaysis_integrations`, `vaysis_invitations`, `vaysis_notifications`, `vaysis_user_roles`, `conversations`, `messages`.
- Sunucu fonksiyonları: `chatbot`, `starvay-import`. Döngü tespiti (A→B→C) için tablo, RPC veya fonksiyon adı yok. Site "A→B→C … döngülerini otomatik tespit eden eşleşme motoru" yazar; motor istemcide görülmedi, sunucuda olup olmadığı bilinmiyor → **doğrulanamadı**.
- Prototip işaretleri: "Bu sayfa sadece test amaçlıdır."; "Belge yükleme özelliği yakında aktif olacak"; "demo doğrulama"; yer tutucu adres "Maslak Mah. Büyükdere Cad. No:123"; "Yeni üyeler sisteme katıldıkça eşleşme şansınız artacaktır" (ağ henüz ince).
- Ödeme: "Banka transferi ile yaptığınız ödemeyi sisteme bildirin" → kalan net bakiye sistem dışı havale ile ödenir; platform ödeme kuruluşu değil.

## 4. Tek sistem adım 1 ile karşılaştırma

| Ölçüt | Tek sistem adım 1 | Vaysis | Eşleşme |
| --- | --- | --- | --- |
| Nesne | e-fatura alacağı/borcu | onaylı fatura alacağı (e-fatura, ERP) | aynı |
| Kapalı döngü mahsup | evet | iddia: A→B→C; kanıt: yok | iddia aynı, kanıt yok |
| Nakit dolaşmadan | evet | mahsup kanalı evet; satış kanalı nakit | kısmen |
| Kapsam | sistem (tüm lira alacak-borç) | gönüllü üyelik, ağ ince | farklı |
| Hukuki araç | belirtilmemiş | TBK temlik, ikili e-imza | Vaysis somut |
| Kalan net borç | ödeme planı (adım 2) | sistem dışı havale, bildirim | farklı |
| Faizin durması (adım 3) | evet | yok | yok |
| Endeksli senet (adım 4) | evet | yok | yok |
| Kira (adım 5) | evet | yok | yok |
| Ölçülmüş sonuç | yok (akış 0,4270 `baska_nesne`) | yok (hacim bulunamadı) | ikisi de boş |

## 5. Okuma (yorum; ölçüm değil)

- Vaysis, adım 1'in nesnesini (fatura alacağı) ve aracını (döngü mahsubu) aynı seçmiş tek Türk kayıt. Mekanizmayı somutlaştırdığı yer hukuki araç: temlik zinciri + e-imza. Tek sistem metninde bu katman yok; bir sistem kurulacaksa bu soru burada cevaplanmış.
- "Yeni üyeler katıldıkça eşleşme şansınız artacak" cümlesi, bu depodaki gedikle aynı: firma çifti yok, KAP kenarı 0 (`nace_kap_sonuc.json`). Mahsup ağ yoğunluğuna bağlı; gönüllü üyelikte ağ ince kalmış görünüyor. Bu bir gözlem; neden-sonuç ölçülmedi.
- Yan kanal (alacak satışı, Fatura Pazarı) mahsubu faktoringe yaklaştırır; nakit girer, "nakit dolaşmadan" cümlesi o kanalda geçerli değil.
- Faaliyet dışı kaydı ile canlı site çelişiyor; sonuç çıkarılmaz.

## Ne denmez

- "Vaysis mahsubu çalıştırdı" denmez: hacim, üye, tutar yok.
- "Vaysis battı, mahsup çalışmaz" denmez: faaliyet dışı kaydı var, neden yok; site canlı.
- "Döngü motoru var" denmez: iddia var, kod istemcide yok, sunucu görülmedi.
- Vaysis tek sistemin önceli denmez; kişilere veya şirkete niyet atfedilmez.
