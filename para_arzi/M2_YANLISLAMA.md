# M2 etkisi — yanlışlama ölçütleri

Bu dosya hesap çalışmadan yazıldı. `m2_etki.py` sayıyı ancak bu kurallarla üretir. Ölçüt değişirse json'daki `kriter_sha256` tutmaz.

Kaynak sınırı: TCMB EVDS3, anahtarsız uç, grup `bie_hpbitablo1` (Para Arzı, haftalık cuma). Dönem, 2026-Q1'e en yakın yayımlanmış cuma. Birim, repodaki para-banka serileriyle aynı kural: ham / 1e6 = milyar TL (bin TL → milyar). Bu kural, 2026-03 `TP.KM.E041 + TP.KB.FON033` hamının / 1e6 sonucunun repodaki 8.037,1 milyar TL hane TL mevduatıyla örtüşmesiyle sınanır. Örtüşmezse birim yanlışlanmıştır; M2 düzeyi yazılmaz.

## Düzey

- **M2.** `TP.HPBITABLO1.11`. TL kısmı = dolaşımdaki para (`…1.3`) + vadesiz TL (`…1.4`) + vadeli TL (`…1.12`). YP kısmı = vadesiz YP (`…1.8`) + vadeli YP (`…1.15`).
- **Yanlışlama.** TL kısmı + YP kısmı, yayımlanan M2'den 0,05 milyar TL'den fazla saparsa bileşen listesi yanlış okunmuştur; düşüş yüzdesi üretilmez.
- **M3 kontrolü.** M3 (`…1.18`) = M2 + repo (`…1.19`) + para piyasası fonu (`…1.20`) + ihraç edilen menkul (`…1.21`). Aynı tolerans. Menkul satırı M2 toplamının içinde bir toplanan değildir.

## 16.472,8 milyar TL

Repodaki TL para stoku = TCMB F.2 para (emisyon, 898,3) + HPB tablo 3 yurt içi TL mevduat (`TP.HPBITABLO3.2`, 15.574,5). `adim45_birim.py` bu toplamı «M1 değildir» diye yazar.

- **Yanlışlama (eşitlik iddiası).** Aynı çeyrekte M2 = 16.472,8 çıkarsa «TL para stoku M2'dir» ayakta kalır. Çıkmazsa iddia düşer. Farkın gerekçesi ancak şu üç kanaldan yazılır: emisyon banka kasasını içerir, dolaşımdaki para içermez; tablo 3'ün TL mevduat kapsamı M2'nin TL mevduat satırından ayrıdır; M2 YP mevduatı içerir, 16.472,8 içermez. Kapsam ölçülmeden fark uydurulmaz.

## Senet M2'nin dışında mı

Adım 4'ün kendi SFC satırı: tutucunun VF.2'si (mevduat) düşer, VF.3'ü (kâğıt) artar. İhraççı K′ varsayımdır.

- **Yanlışlama.** Menkul kıymet, M2 bileşen listesinde bir toplanansa senet M2 dışındadır denmez. Liste yalnız para ve mevduatsa (TL ve YP) senet M2 dışındadır: **kanıt**, tanım gereği.
- Hazine kâğıdı ile banka ihraçlı menkul ayrımı: M3'teki «ihraç edilen menkul» stoku, repodaki 2026-03-27 DİBS stokundan (10.339,8 milyar TL, `rev_adim4_sonuc.json`) bir mertebe küçükse bu satır DİBS stoğu değildir. Hazine kâğıdı o satıra da girmez; banka kâğıdı girer. İkisi de M2 toplananı değildir. Ayrım ölçülmezse ihraççının hangisi olduğu M2 hükmünü değiştirmez.

## Adım 4 — birinci tur (stok)

Adres ham toplam 19.361,9 = 8.322,4 + 4.400,1 + 6.639,4. Çift sayım bandı repodan okunur, yeniden tahmin edilmez: alt örtüşme 285,3 (ZP8 − hane TL mevduatı), üst örtüşme 6.639,4. M2'ye giren ayrı stok:

- alt A = 19.361,9 − 6.639,4 = 12.722,5
- üst A = 19.361,9 − 285,3 = 19.076,6

Ham 19.361,9 M2 tabanına yazılmaz.

YP mevduat M2 bileşeniyse adresin YP ayağı da M2'den çıkar; değilse yalnız TL ayak çıkar. Karar, tablo 1 listesine göre verilir. VF.2 ZP8 ile HPB mevduatının birebir aynı çevre olduğu ölçülmediği için θ × A → M2 düşüşü **aday**dır; A'nın aritmetiği **kanıt**tır.

- Tepe (senet eldeyken) = θ × A. θ ∈ {0,1; 0,25; 0,5}. χ tepeyi değiştirmez.
- Kalıcı (vade sonu, 8 çeyrek) = χ × tepe. χ ∈ {0; 0,5}. χ = 0 ise (1−χ) mevduata döner, kalıcı birinci tur 0'dır. Bu, `adim4_adres_yonlendirme.py` çıkış kuralıdır.

## Adım 4 — ikinci tur (ayrı satır)

Kredi daralması = 0,08 × eldeki senet stoku, yıllık. 0,08 `tek_sistem_kademe.py` sabitidir, ölçülmüş eğim değildir (`rev_adim4`: tarihsel eğim ayrı bant, nedensellik değil).

- Tepe yıl: 0,08 × tepe. χ'ye bağlı değildir.
- Vade sonu: 0,08 × kalıcı stok. χ = 0 ise bu satır da 0'dır.
- **Aday varsayım:** eksik kredi 1:1 eksik mevduat yaratımıdır. İkinci tur bir kez yazılır; 0,08² ve sonsuz çarpan yazılmaz.
- İkinci tur akıştır (milyar TL/yıl). Stok toplamına eklenmez. Eklenirse birim yanlışlanmıştır.

## Adım 1–2

İki sütun: araç ayrı, araç birleşik. Kenarlar `stok_silim.py` metin listesidir.

- **Mahsup 0,421.** Nesne, aylık brüt servis akışıdır; `optimal_mahsup` net pozisyonu sabit tutar (`mahsup_sektor_ozet.json`). Net pozisyon sabitse mevduat stoku değişmez. İki sütunda da mevduat ayağı 0, M2 düşüşü 0. **Yanlışlama:** mahsup çıktısı bir mevduat stokunu düşürüyorsa bu satır 0 yazılmaz.
- **Stok silimi.** Araç ayrıda silinen 0 (`stok_silim_sonuc.json`); H–PFK ve F–PFK mevduat karşı bacağı yapısal 0'dır. Mevduat ayağı 0, M2 düşüşü 0.
- Araç birleşikte silinen = min(iki yön). Mevduat ayağı, silinen tutarın mevduat olan kısmıdır. Yönlerden biri yalnız mevduat, diğeri yalnız kredi ise mevduat ayağı = silinen (öncelik belirsizliği bu üç çiftte ısırmaz). Yurt içi ayak: F→PFK ve H→PFK mevduatı. PFK→ROW mevduatı, alacaklı PFK ve borçlu ROW ise yurt dışı varlıktır, Türkiye M2'si değildir.
- Birleşik yurt içi ayağın M2'ye 1:1 yazılması **aday**dır: PFK bankadan ayrılmamıştır, metin kısmi çifttir, H-S bu sütunu skorlamaz. **Yanlışlama:** araç ayrıda mevduat silineni 0 değilse «ayrı sütun 0» düşer. Birleşik yurt içi ayak 7.195 + 6.772 değilse aritmetik düşer.

## Adım 3, 4.5, 5

- **Adım 3.** Nesne, F.4 kredi stoku üzerindeki faiz tahakkukudur; anapara ve mevduat stoku dosyada düşmez. Doğrudan M2 düşüşü 0. Faizin ödenmemesinin mevduatı hangi yönde oynatacağı (banka kârı sermayeye yazılırsa M2 görece yüksek kalır) ölçülmedi. Dolaylı tutar yazılmaz. **Yanlışlama:** adım 3 çıktısı bir mevduat stokunu eksiltirse 0 yazılmaz.
- **Adım 4.5.** λ = 1 iken TL_yeni = TL_eski (`ADIM45_BIRIM.md`). Doğrudan M2 düşüşü 0. **Yanlışlama:** λ = 1 iken TL stoku değişiyorsa 0 yazılmaz.
- **Adım 5.** Aktarım Ho → Ha, ikisi de hane. İki yerleşik mevduat arasındaki aktarım M2'yi değiştirmez. Doğrudan 0. **Yanlışlama:** taraflardan biri para tutan sektörün dışındaysa (yurt dışı ev sahibi gibi) 0 yazılmaz. Repoda iki taraf da H'dir.

## Üç senaryo (hesaptan önce kilitli)

| Senaryo | θ | χ | Adres | Adım 1–2 M2 |
| --- | --- | --- | --- | --- |
| düşük | 0,1 | 0 | 12.722,5 | araç ayrı: 0 |
| orta | 0,25 | 0,5 | 19.076,6 | araç ayrı: 0 |
| yüksek | 0,5 | 0,5 | 19.076,6 | araç birleşik yurt içi ayak, aday |

Başlık toplamı stoktur: adım 1–2 + adım 4 kalıcı birinci tur + adım 3/4.5/5 doğrudan. Tepe ve ikinci tur aynı tabloda ayrı satırdır, başlığa girmez.

Yüzde = milyar TL / ölçülen M2 × 100. M2 ölçülmeden yüzde yazılmaz.
