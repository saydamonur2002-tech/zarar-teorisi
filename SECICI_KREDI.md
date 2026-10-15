# Seçici kredi modeli: Türkiye kalibrasyonu

Çalıştır: `python3 secici_kredi_kalibre.py`. Model: `secici_kredi.py` (Google Sheet "Secici_Kredi_Veri_DOLU" formüllerinin birebir taşınması; tablonun Sim_S1-S4 ve ölçüm paneli sonuçlarıyla parite testi var). Kalibrasyon iki katmanlı ve her parametre etiketli.

## 1. Çapalar: ölçülebilen başlangıç durumu (t0 = 2025)

| Parametre | Tablodaki temsilî değer | Türkiye çapası | Sınıf | Kaynak |
| --- | ---: | ---: | --- | --- |
| `pi0` | 0.300 | 0.309 | olcum | V24 TÜFE Aralık/Aralık |
| `om0` | 0.500 | 0.600 | tahmin | V01/V15; V01 tabloda GSYH×0,600 (TÜİK 2023-24 oranı) |
| `cad0` | 0.040 | 0.019 | olcum | V16/V15 (C1 göstergesi) |
| `X0` | 30.000 | 25.999 | tahmin | V17/V15; V17 tabloda (mal+seyahat)×1,25×kur |
| `nfp` | 0.015 | 0.015 | tahmin | V20/V15; ikincil gelir dahil vekil |
| `Cf0` | 42.000 | 38.880 | tahmin | A1 × Yh0; V02 tabloda tahmin |
| `D10` | 4.000 | 3.526 | tahmin | V03/V01 × Yh0 toplam; H1/H2 bölüşümü 0,4/0,6 ölçülemedi |
| `D20` | 6.000 | 5.289 | tahmin | V03/V01 × Yh0 toplam; H1/H2 bölüşümü 0,4/0,6 ölçülemedi |
| `cc` | 0.150 | 0.082 | olcum | (ΔV10 − bireysel kredi artışı)/V15 |
| `ccp_ref` | 0.030 | 0.047 | olcum | A2 (V03−V04)/V01 |
| `G0` | 0.180 | 0.199 | olcum | (V28 − V25)/V15 faiz hariç merkezi yönetim gideri |
| `mx` | 0.400 | 0.669 | tahmin | C2 = V18/V17 (Kavram_Gösterge: C2 ↔ mx); iç satışa giden ara girdiyi de içerir, üst sınır |
| `mc` | 0.200 | 0.071 | kalibre | t0 ithalat kimliği: ortak ölçek ×0.355 |
| `mi` | 0.450 | 0.160 | kalibre | t0 ithalat kimliği: ortak ölçek ×0.355 |
| `mg` | 0.100 | 0.035 | kalibre | t0 ithalat kimliği: ortak ölçek ×0.355 |

Z0 (t0 talep tutarlılığı kalemi) yeniden hesaplandı: -8.7769 (tablodaki 0,3468).

Ölçülemeyenler tablodaki temsilî değerinde bırakıldı: `ph1` ve `th1` (alt gelir grubunun taban ve gelir payı: V37 boş), `inv0`, `b`, `spread`, `am`, `sig`, `rn`, eşikler (k1s...k6c). Bunlar kalibre DEĞİL. `mc`, `mi`, `mg` ayrı ayrı ölçülemedi; yalnızca ortak ölçekleri t0 ithalat kimliğinden geldi, oranları birbirine göre tablodaki gibi.

## 2. Davranış parametreleri: anket yolu üzerinde ayar

Hedef: PKA ve `bes_yil_senaryo.csv` yıl sonu beklentileri. t=1 → 2026. İçeri örnek: 2026-2027 TÜFE, politika faizi, kur (6 moment). Örnek dışı: 2028 TÜFE ve faiz, 2031 TÜFE. Serbest: alpha, pt, rho (davranış), S1 kolunun tay ve cred'i. 5 serbest parametre, 6 moment: neredeyse tam belirlenmiş; bu ayardır, kestirim değil. Hedefin kendisi bir anket (tahmin), gerçekleşme değil.

| Parametre | Tablodaki | Kalibre |
| --- | ---: | ---: |
| `alpha` | 0.800 | 0.756 |
| `pt` | 0.250 | 0.346 |
| `rho` | 0.500 | 0.487 |
| `tay` | 0.500 | 0.274 |
| `cred` | 0.300 | 0.272 |

| Gösterge | Yıl (t) | Hedef | Kalibresiz hata | Kalibre hata | Örnek |
| --- | --- | ---: | ---: | ---: | --- |
| pi | 2026 (1) | 0.296 | -0.054 | -0.028 | içi |
| pi | 2027 (2) | 0.227 | -0.034 | -0.015 | içi |
| i | 2026 (1) | 0.351 | 0.042 | -0.011 | içi |
| i | 2027 (2) | 0.272 | 0.075 | 0.027 | içi |
| dep | 2026 (1) | 0.203 | -0.018 | -0.019 | içi |
| dep | 2027 (2) | 0.136 | 0.132 | 0.023 | içi |
| pi | 2028 (3) | 0.183 | -0.047 | -0.025 | dışı |
| pi | 2031 (6) | 0.121 | -0.084 | -0.080 | dışı |
| i | 2028 (3) | 0.224 | 0.048 | 0.018 | dışı |

Hata = model − hedef. İçeri hatalar sıfıra yakınsa bu uydurmanın doğal sonucudur. Örnek dışı satırlar asıl bilgidir.

## 3. Tablonun kendi sınaması (Eleştiri #12): geçmişi üretebiliyor mu?

Kalibre davranış parametreleriyle, t0 = y için tablodaki çapalar yıl y verisinden kurulur ve y+1 TÜFE'si tahmin edilir; naif tahmin TÜFE(y).

| Yıl | Gerçek TÜFE | Model | Naif (önceki yıl) | Model hata | Naif hata |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2018 | 0.203 | 0.120 | 0.119 | -0.083 | -0.084 |
| 2019 | 0.118 | 0.178 | 0.203 | 0.059 | 0.085 |
| 2020 | 0.146 | 0.107 | 0.118 | -0.039 | -0.028 |
| 2021 | 0.361 | 0.147 | 0.146 | -0.214 | -0.215 |
| 2022 | 0.643 | 0.312 | 0.361 | -0.330 | -0.282 |
| 2023 | 0.648 | 0.658 | 0.643 | 0.010 | -0.005 |
| 2024 | 0.444 | 0.592 | 0.648 | 0.148 | 0.204 |
| 2025 | 0.309 | 0.385 | 0.444 | 0.076 | 0.135 |

Ortalama mutlak hata: model 0.120, naif 0.130.

## 4. Senaryolar: kalibresiz ve kalibre

S1 kalibre kolla, S2-S4 tablonun politika kollarıyla (davranış parametreleri ortak). Dar Koridor skoru ve ana göstergeler:

| Senaryo | Kal. | Enflasyon t=1 | t=5 | t=10 | t=20 | Cari açık t=5 | Koridor t=1 | t=10 | t=20 | Rejim t=20 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| S1 | önce | 0.242 | 0.045 | 0.028 | 0.043 | 0.035 | 78.4 | 44.8 | 45.4 | Daralan koridor |
| S1 | sonra | 0.268 | 0.072 | -0.037 | -0.108 | 0.012 | 43.7 | 46.5 | 33.1 | Daralan koridor |
| S2 | önce | 0.105 | 0.027 | 0.024 | 0.026 | 0.034 | 67.5 | 49.6 | 49.5 | Daralan koridor |
| S2 | sonra | 0.081 | 0.052 | 0.023 | 0.005 | 0.012 | 37.5 | 21.3 | 17.8 | Geniş koridor |
| S3 | önce | 0.150 | 0.097 | 0.087 | 0.055 | 0.047 | 49.8 | 16.0 | 2.2 | Geniş koridor |
| S3 | sonra | 0.129 | 0.110 | 0.078 | 0.047 | 0.013 | 21.0 | 7.7 | 1.5 | Geniş koridor |
| S4 | önce | 0.214 | 0.159 | 0.186 | 0.211 | 0.055 | 67.4 | 52.4 | 53.8 | Daralan koridor |
| S4 | sonra | 0.198 | 0.137 | 0.151 | 0.156 | 0.027 | 39.0 | 42.8 | 46.1 | Daralan koridor |

**Uyarı.** Kalibre yolda negatif enflasyon çıkıyor: S1 t=8, S1 t=9, S1 t=10, S1 t=11, S1 t=12, S1 t=13 .... Uzun vadede enflasyon hedefe değil hedefin altına gidiyor; bu modelin yapısal sınırıdır (TL değer kaybı −%10 tabanına bağlanıyor, beklenti hedefe çıpalı), kalibrasyon bunu düzeltmez.

Karşılaştırma: ölçülmüş Dar Koridor Basınç Endeksi 2025 = 32.5 (Geniş koridor; 12 gösterge, kapsam %60). Simülasyonun `kor` skoru 6 bileşenlidir, ölçümün 22 göstergeli DKBE'si farklı bir bileşimdir; ikisi birebir kıyaslanmaz.

## Ne denmez

- Model Türkiye için tahmin üretir denmez. Davranış parametreleri bir anket yoluna ayarlandı, gerçekleşmeye değil.
- 'Kalibre' sözü, parametrelerin tamamı için kullanılmaz: yalnızca yukarıda 'olcum' ve 'tahmin' işaretli çapalar ile 5 davranış parametresi için.
- Seçici kredi, ücret ve yerlileşme kanalları (sp, leak, disc, socw, wr, rek, mu, lloc, tfpk, locmax) ölçülemedi; S2-S4 farkları büyük ölçüde bu temsilî değerlerin sonucudur.
- Teşvik skorkartı, kurtarma sırası ve sektörel net döviz sayfaları kurgusal firma/sektör satırlarıyla geliyor; veri olmadan bu modüle taşınmadı.
- S3 ile S4 farkı (kurumsal disiplin) bir varsayımdır; model bunu ölçmez.
