# Model kusurları — revize değerlendirme

Bu dosya, depodaki teknik notların (`OKU.txt`, `VARSAYIM_UYARISI.md`, test özetleri) sentezidir. **Politika reçetesi değildir**; kapalı muhasebe iskeletinin neyi iyi gösterdiğini ve nerede zayıf kaldığını netleştirir.

## Merkezi kusur

**Asıl sınır, kapalı muhasebe iskeletinin hem gücü hem tavanı olmasıdır:** her kaybın bir yerde oturması gerektiğini gösterir; fakat kaybın **neden**, **ne zaman** ve **nasıl tanındığını** (veya tanınmadığını) davranışsal ve kurumsal olarak açıklamaz. Stok-akış kimliği kapanabilir; tanıma gecikmesi, forbearance, regülasyon ve beklenti dinamiği modele gömülü değildir.

**Güç:** Temerrütün sıfır toplamlı olmadığı, F değerleme zararının banka provizyonuna otomatik geçmediği, yükün biriktiği ve kamu desteğine dayandığı muhasebe gerçeği görünür kalır.

**Zayıflık:** Sonuçların büyük kısmı **elle konmuş paylara**, **eksik kırılımlara** ve **zayıf kalibre edilmiş zarar geçişine** bağlıdır; “yanlış sonuç”tan çok **belirsizlik bandı geniş** demektir.

---

## 1. Varsayım yükü yüksek, ölçüm zayıf

| Konu | Durum | Sonuç kayarsa |
| --- | --- | --- |
| Ha borç payı (`D_A_BASE`) | **Varsayım.** Taban **%40** (`hane_alt.py`); ilk kullanıcı girdisi %70’ti, gözlenen stres bandının (%17–44) üstündeydi. %70 duyarlılıkta kalır. Duyarlılık tablosunda `satir_tipi`: **taban** \| **duyarlilik** (`akis_model_ozeti.json`, `hane_alt_duyarlik.csv`). | `lambda_B`, ödenemez borç, L senaryoları |
| VYS hane payı | **Varsayım** (%40 taban; bireysel ~%80 portföy) | VYS kanalı, “rapor dışı yük” |
| Mükellef–hazne (bütçe) | **Varsayım**; MV sınıflaması kapanır, payer kapanmaz | K′ kanalı, vergi yükü payları |
| Gecikme faizi / tahsilat | **Varsayım** (%63,2; kısmi ödeme yok) | Çift kayıt “borçlu fazlası” |
| SYR / sermaye eşiği | **Doğrulanmadı** (%16,5 eski girdi; %12 asgari varsayım) | Serbest sermaye, tanıma tavanı |
| Bireysel iflas | **Doğrulanmadı** (borç silinmez varsayımı) | Temerrüt = net kayıp |

Halk dili: “Yük stoku var” iddiası panel ve BDDK ile uyumlu olabilir; **“tam olarak ne kadar ve kimde”** sorusunun cevabı çoğunlukla model verisinden değil, işaretlenmiş paylardan gelir. Ayrıntı: [`VARSAYIM_UYARISI.md`](VARSAYIM_UYARISI.md).

---

## 2. Lambda (zarar geçişi) ampirik olarak zayıf

**F → B (değerleme → provizyon):** `kalibre_lambda.py` — GSYH normalize regresyon; beta negatif ve anlamsız; θ ≈ −0,03 ± 0,02 → üst sınır ~**%1,4** geçiş. **≥%4 geçiş reddedilir** (güçlü sıfır). Bu, “F zararı F’de kalır / tanınmaz” önermesi ile **tutarlı**; nedensel kanıt değil (BDDK kuralları, enflasyonla erime alternatifleri açık).

**F → K (~%24):** `OKU.txt` içinde **geri çekildi** — nominal ikinci tur bulgusu GSYH normalize edilince kayboluyor; ortak trend ürünü olabilir. **Simülasyonda F→K ~0,24 kullanılmamalı.**

**Zaman boyutu:** Tanıma oranı **s** (II. Grup → TGA hızı) kalibre edilmedi (`kalibre_lambda_rapor.py`). Durum-bağımlı **lambda_B** yalnızca sektör toplamı + sermaye tavanı mantığıyla **senaryo** üretir.

**Özet:** SFC kimliği kapanır; **lam / kappa genel olarak tanımlanamaz** — yalnızca “provizyona geçiş çok düşük” yönünde sınırlı ampirik destek. Default-kaskad simülasyonu bu parametre olmadan **bulgu** olarak okunmamalı (`OKU.txt`, `SIMULATOR` notu).

---

## 3. Matrisler ekstra bilgi eklemiyor

Geriye dönük test (`entegre_ve_test.py`, `geri_test_ozeti.json`):

| Yöntem | R² (borçlu değerleme → alacaklı) |
| --- | ---: |
| Orantılı **Lm** | 0,868 |
| Basit varlık payı | 0,862 |
| Döviz ağırlıklı | 0,565 |
| Bilateral D kısıtı (**L_bil**) | 0,856 |

**Lm**, kuruluş varsayımının (alacaklı payına böl) ötesinde anlamlı tahmin gücü eklemiyor. **L / Lm** kapalı muhasebe dağıtımıdır; **ölçülmüş fatura ağı değildir** (`ODEME_ZINCIRI.md`). Kimden kime **gerçekten** aktığı bilinmiyor; dağıtım sözleşmesel.

---

## 4. Eksik veri ve kapsam

- **Hisse / FDI / para birimi kırılımı yok** → D kur değerlemesi büyük kur dönemlerinde **sistematik düşük** (2025-Q4: gözlenen ~1,92 trilyon TL, tahmin ~0,99–1,12).
- **K′ ⊃ merkezi yönetim değil:** SGK, yerel yönetim, TCMB tam seti yok; bütçe dengesi ile K′ net akış **fark korelasyonu −0,15**.
- **Hane desili, resmi TGA satış serisi, satılan havuz karşılık düzeyi** eksik veya haber derlemesi.
- **2010–2020 D uyumsuzluğu** (altın/SDR) **U**’da; neden doğrulanmadı.
- **Banka kredi zararı / BDDK** kısmen var; tam hane–firma desili yok.

Bunlar “model yanlış” demek değil; **modelin gördüğü şey sınırlı** demektir. Açık liste: `OKU.txt` satır 77 (`ACIK:`).

---

## 5. Minsky tarafı muhasebe düzeyinde kalıyor

Minsky’nin motoru: risk iştahı, hedge → spekülatif → Ponzi geçişi, beklenti kırılması, **Minsky moment** (roll-over kesilmesi). Bu depo:

- **Stok-akış + tanınmayan yük + servis/gelir eşikleri** (`uc_kural_senaryo`, `ponzi_egilim`, `MINSKY_GUNCEL_KARSILASTIRMA.md`) ile rejimi **dolaylı** okur.
- **Endojen risk iştahı, forbearance, regülasyon tepkisi, likidite/solvency ayrımı** dinamik olarak modellenmez.
- Senaryolar (tanıma, faiz birikimi, limit dondur) **statik veya basit zaman yayılımı**; kriz tetikleyicisi atanmaz.

**Okuma:** “Minsky noktası” burada **tanıma eşiği** veya **nakit akışı bağının koptuğu an** proxy’sidir; tam döngü teorisi değildir. SFC iskeleti Minsky’yi **bilanço diline** çevirir; **psikolojik/kurumsal motoru çalıştırmaz**.

---

## Kısa tablo: kusur → depo cevabı

| Kusur | Depoda nerede | Düzeltme / sınır |
| --- | --- | --- |
| Pay varsayımları | `hane_alt.py`, `VARSAYIM_UYARISI.md` | Taban %40; duyarlılık tabloları; etiket **senaryo** |
| Lambda zayıf | `kalibre_lambda_*.json`, `OKU.txt` T3 geri çekme | Provizyona geçiş düşük; F→K kullanma |
| Lm bilgi eklemez | `geri_test_ozeti.json`, `OKU.txt` T2 | Matris dağıtım varsayımı olarak oku |
| Veri kırılımı | `ACIK` listesi, D kur hatası | Idempotent uyarı; tahmin bandı geniş |
| Minsky mekanik | `MINSKY_GUNCEL_KARSILASTIRMA.md` | Moment tarihi yok; eşik proxy |

---

## Ne denmez

- “Model Türkiye’nin resmi projeksiyonudur.”
- “Lambda_B = 0,59 kesin tanıma oranıdır.” (%70 **duyarlılık** satırı.)
- “Lm matrisi gerçek borç ağını ölçtü.”
- “Minsky moment 20XX’te geçti.” (depo takvim üretmez.)

Güncelleme: bu metin repo test çıktılarıyla hizalanır; sayılar değişirse önce `OKU.txt` / `*_ozeti.json`, sonra bu dosya güncellenmelidir.
