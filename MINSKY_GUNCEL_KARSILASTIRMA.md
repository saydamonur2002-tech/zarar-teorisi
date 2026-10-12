# Minsky rejimi — güncel veri vs model proxy

**Tarih:** 2026-10-12 (EVDS köprü: `acik_veri_ozet.json`). **Minsky moment tarihi yoktur**; bu tablo rejim karşılaştırmasıdır. Modelin Minsky tarafının sınırı: [`MODEL_KUSURLARI.md`](MODEL_KUSURLARI.md) §5.

## 1. Minsky rejimleri (teori)

| Rejim | Nakit akışı | Kopuş ne zaman? |
| --- | --- | --- |
| **Hedge** | Gelir **faiz + anapara**yı karşılar | Roll-over şart değil |
| **Speculative** | Gelir **faizi** karşılar; anapara yeniden borçlanır | Faiz ↑, vade kısalır, kredi hattı kapanınca |
| **Ponzi** | Gelir **faizi karşılamaz**; **yeni borç** eskiyi öder | Yeni kredi/kart hattı **durunca** (Minsky moment) |

Kopuş **tek % eşiği** değil; **finansmanın kesilmesi** + varlık fiyatı / gelir şoku.

---

## 2. Modeldeki parametre eşikleri (senaryo; Minsky ölçümü değil)

Kaynak: `uc_kural_senaryo.Params` — **Ha aylık servis / net taban gelir proxy**.

| Band | Eşik | Senaryoda etki |
| --- | ---: | --- |
| Hedge | servis/gelir **≤ %30** | Tüketim kredisi büyümesi tam çarpan |
| Speculative (ara) | **%30–40** | Büyüme ×0,4 |
| Ponzi (etiket) | **> %40** | Büyüme ×0,05 |

Proxy formül: Ha borç payı **%40 varsayım** × (kart+teminatsız+konut stoku) × **%35/yıl servis** / (sabit asgari × N_A).

---

## 3. Güncel karşılaştırma tablosu

| Boyut | Minsky okuma | Model (2026-Q4 giriş, `mevcut`) | Güncel ölçüm (EVDS / depo) | Uyum |
| --- | --- | ---: | ---: | --- |
| **Gelir yeterliliği (taban)** | Hedge için gelir borç servisini karşılamalı | Kapsama **%57,4** (donuk taban) | Asgari **28.076 TL** / bekar yaşam **48.885 TL** → **%57,4** | Aynı taban |
| **Ha servis / gelir** | Hedge <%30; Ponzi alegori >%40 (model) | **%47,3** → **ponzi bandı (parametre)** | **Doğrudan ölçülmedi** | Proxy yüksek; hane ortalaması bilinmiyor |
| **Taksit / gelir (kart hariç)** | Speculative/Ponzi için stok×faiz yükü | Modele **girmez** | 2024 stok/gelir **%7,5**; 18 yıl vade varsayımı → taksit/gelir **~%4,0** (`hane_taksit`) | Ölçüm **daha düşük** (kart yok; gelir tanımı farklı) |
| **Yeni borçla büyüme (Ponzi imzası)** | Ponzi = yeni borç eskiyi besler | `mevcut`: kart **~%46/yıl**, tüketici **~%43/yıl** (EVDS) | BDDK 13 ay: kart **+45,9%**, tüketici **+43,3%** (2026-09 vs 2025-08) | **Uyum:** stok hızla büyüyor |
| **Roll-over kesilmesi** | Minsky moment tetikleyici | Yalnız **sert/revize** senaryoda kredi tavanı | Henüz **ölçülmemiş** (spreads, red oranı, limit kesintisi serisi yok) | Kopuş **tarihi atanamaz** |
| **Temerrüt (dar)** | Stres gecikmesi | `limit_dondur` yalnız kilitli senaryoda | Takipteki / stok **G1 hane ~%5,09** (2026-09) | Banka tablosu **henüz sınırlı** stres |
| **Temerrüt (geniş)** | Yakın izleme = erken Ponzi | Modele **yok** | OKU: G3 hane **~%20–28** (Yİ dahil; tanım geniş) | **Çelişki riski:** dar %5 vs geniş %20+ |
| **Takip stok / tüketici stok** | Stok kalitesi | Rant/direnc proxy | EVDS **~%13** (2026-10) | Orta; G1 oranından yüksek (stok tabanı) |
| **Firma finans yükü** | Speculative (faiz yükü, roll-over) | F kanalı senaryoda | 2024 finansman/faaliyet **0,839** (Sektör Bilançoları) | **Spekülatif baskı** (ölçüm, 2024) |
| **Enflasyon** | Reel gelir erimesi | `mevcut` taban **donuk** | TÜFE yıllık **~%30,7** (EVDS; seri ayı 2026-01) | Reel taban **erir** (senaryo mevcut bunu modeller) |

---

## 4. “Nokta ne zaman kopar?” — güncel veriyle cevap

| Soru | Güncel veri ne diyor? |
| --- | --- |
| **Şu an hedge mi?** | **Karışık.** Banka takip oranı **düşük (~%5)**; ama **kredi stoku çok hızlı büyüyor (~%43–46)** ve model Ha proxy **%47 servis/gelir** → **roll-over’a bağımlılık yüksek** (Minsky speculative–ponzi arası **davranış**, sınıflama değil). |
| **Kopuş oldu mu?** | **Hayır (dar tanım):** sistemik takip dalgası ve kredi durması **ölçülmedi**. |
| **Kopuş neye yakın?** | **Ponzi imzası:** yüksek stok büyümesi + yüksek faiz ortamı (`hane_taksit` 2024 faiz stok **~%53**). **Tetik:** kart/limit/kredi **büyümesinin durması** veya faiz şoku — depo **tarih vermez**. |
| **Model vs ölçüm** | Model **%47** der; **hane_taksit ~%4** der — **aynı nesne değil** (Ha+agregat servis vs kart hariç stok/gelir). İkisi birlikte: **borç stoku ve faiz yükselirken, agregat taksit oranı henüz düşük görünebilir** (vade uzun, kart ayrı, gelir tanımı geniş). |

---

## 5. Ne denmez

- “Türkiye **Minsky moment’i 20XX’te geçti**” — depo **takvim** üretmez.
- Model **%40** eşiği = **resmi kriz eşiği** değil; senaryo parametresi.
- **%5 takip** ile **%47 servis proxy** aynı cümlede **tek stres** sayılmaz (farklı tanım).

---

## 6. Dosya referansları

| Veri | Dosya |
| --- | --- |
| EVDS taban | `acik_veri_ozet.json`, `ACIK_VERI_KOPRU.md` |
| Ha servis giriş | `uc_kural_senaryo.csv` (`mevcut`, 2026-Q4) |
| Takip G1 | `odemeyen_payi_aylik.csv` |
| Taksit/gelir | `hane_taksit_ozeti.json` |
| Eşikler | `uc_kural_senaryo.py` (`hedge_servis_esik`, `ponzi_servis_esik`) |

Güncelleme: `python3 acik_veri_kopru.py`
