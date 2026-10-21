# Politika kırılması — 2026-10-21 kutu çıktıları

21 Ekim 2026 kutu analizinin olduğu gibi kopyası. Sayılar, etiketler (`[VERİ]` / `[VEKİL]` / `[HESAP]` / `[TAHMİN]` / `[İKİNCİL]` / `[DOĞRULANMADI]`, kanıt / aday / tahmin) ve hükümler kaynak klasörlerdeki `ON_KAYIT.md`, `rapor.md` ve csv/txt çıktılarındadır; bu dizinde yeniden hesaplanmadı.

**Nedensellik iddiası yok.** Kayıtlar istatistiksel sıralama, örtüşme ve senaryo ızgarasıdır.

**EVDS3 anahtarsız ön yüz.** Çekimler `evds3.tcmb.gov.tr/igmevdsms-dis` ön yüzüne beyan edilmiştir. `EVDS_API_KEY` okunmaz. Anahtar isteyen uç ve TÜİK engeli kullanılmadı. Bu kopya yeni veri çekmez.

## Ham veri boyutu

Tek dosya eşiği 5 MB tarandı. En büyük dosya `cipa_kur_hep/ortuk_cipa/er/2016IV.txt` (yaklaşık 878 KB). Eşiği aşan dosya yok; ham json, csv, html ve metin dökümlerinin tamamı duruyor. Dışarıda bırakılan ham dosya yok.

## Klasörler

- `cipa_kok/` — K1–K5 kök testi. `ON_KAYIT.md`, `hesap.py`, `ham/`, `cikti.txt`, `k1.csv`, `k2_phi.csv`, `rapor.md`.
- `cipa_kur_hep/` — “hep kura bağlıydı” kayan pencere. `ON_KAYIT.md`, `hesap.py`, `ham/`, dönem/kırılma metinleri, `kayan_*.csv`, `gecis_*.csv`, `tr_aylik.csv`, `br_aylik.csv`, `rapor.md`.
- `cipa_kur_hep/ortuk_cipa/` — örtük çıpa (TCMB Enflasyon Raporu tahmini). `ON_KAYIT.md`, `hesap.py`, `er/` (2012-I…2016-IV html + metin), `er_tahmin.csv`, `a2_olay.csv`, `b24_12ay_ort.csv`, `cikti.txt`, `rapor.md`.
- `kur_sabit_terim/` — kur denklemi sabit terimi. `ON_KAYIT.md`, `hesap.py`, `ham/` (FRED BRL/MXN/ZAR ve TÜFE), `ceyrek.csv`, `ayristirma.csv`, `cikti.txt`, `rapor.md`.
- `uc_kilit_v2/` — üç kilit yeniden koşuları v2–v3. `ON_KAYIT.md`, `kosu_v2.py`, `kosu_v3.py`, `izgara_gecici.csv`, `izgara_v3.csv`, `kosul_ozet.txt`, `kosul_ozet_v3.txt`, `rapor.md`.
- `uc_kilit_v2/gecis_sabiti/` — α_geçiş ayrıştırması ve koşu v4. `ON_KAYIT.md`, `hesap.py`, `kosu_v4.py`, `ham/`, `pr_panel_2024.json`, `ayristirma.csv`, `model_hatasi.csv`, `izgara_v4.csv`, `cikti.txt`, `ozet_v4.txt`.
- `uc_kilit_v2/atalet/` — kapsam ve sebep. `ON_KAYIT.md`, `hesap.py`, `ham/`, `kapsam.csv`, `sebep.csv`, `cikti.txt`.
- `uc_kilit_v2/karsilama_kredi/` — BDDK hanehalkı kredisi ve koşu v5. `ON_KAYIT.md`, `hesap.py`, `hesap_v2.py`, `k2_duyarlilik.py`, `kosu_v5.py`, `ham/` (BDDK Tablo 4 csv dahil), aylık/dönem csv, `izgara_v5.csv`, `cikti.txt`, `cikti_v2.txt`, `k2_duyarlilik.txt`, `ozet_v5.txt`.

## Bu kopyada yapılmayanlar

- PR #44 (`cipali_uc_kural`) ve PR #37 (`kur_mudahale_c`) dosyalarına dokunulmadı. `pr44_kopya/` arşivde yoktu ve eklenmedi. `uc_kilit_v2/kosu_v2.py`, `kosu_v3.py`, `gecis_sabiti/kosu_v4.py`, `gecis_sabiti/hesap.py`, `karsilama_kredi/kosu_v5.py` ve `k2_duyarlilik.py` yerel `uc_kilit_v2/pr44_kopya/cipali_uc_kural/` kopyasını okur (koşu betikleri `uc_kilit_v2` çalışma dizininden, `gecis_sabiti/hesap.py` kendi dizininden `../pr44_kopya`).
- `kur_sabit_terim/hesap.py` içindeki mutlak kutu yolu göreli yapıldı. Depodaki girdiler: kök `faiz_kur_ham.csv`, `etki_cephesi/git-harm/data/evds_odeme_dengesi_aylik.csv`, kardeş `cipa_kur_hep/gecis_TR_b24.csv`. Kutuda deponun dışında duran `tfv_marj/ham/fred_cpiaucsl.csv` ve `politika_kirilmasi/tcmb_gunluk.csv` bu dalda yok; çekilmedi. Kayıtlı çıktı `ceyrek.csv`, `ayristirma.csv`, `cikti.txt`.
- Çıktılar yeniden üretilmedi.
