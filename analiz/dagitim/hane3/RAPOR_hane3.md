# RAPOR_hane3 — hane satırının alt %40 / orta %40 / üst %20 ayrımı (2014-25 kümülatif, %GSYH reel)
Girdi: ../eksik/tablo_aktor_kanal_tam.csv (hane kanal toplamları aynen; yalnız bölüştürüldü, Σ korunur). Dosyalar: hane3_kanal_grup.csv, anahtarlar.csv, h.py, g.py, hane3.png, ON_KAYIT_hane3.md, SAPMA_hane3.md.

## Anahtarlar (alt/orta/üst)
| Anahtar | alt | orta | üst | Kaynak / etiket |
|---|---|---|---|---|
| gelir payı | 16,7 | 35,7 | 47,6 | TÜİK GYKA 2018 (SBB Gelir Dağılımı ÖİK 2025 Tablo 2) [İKİNCİL] |
| faiz/menkul kıymet geliri | 6,8 | 14,5 | 78,7 | GYKA 2018 gelir türü×beşli (dergipark 2020, TÜİK 2020b) × gelir payı [HESAP/VEKİL] |
| kira (gayrimenkul) geliri | 5,1 | 24,5 | 70,4 | aynı [HESAP/VEKİL] |
| tüketim | 21,5 | 41,1 | 37,4 | TÜİK HBA 2022 [VERİ, yerel gini/hba_tuketim_paylari.csv] |
| ≥1 mn TL mevduat payı (TL / DTH) | üst=37,6 / 55,2 | kalan gelir oranıyla | | BDDK dilim (aylik*.csv, EVDS3 kaynaklı) [VEKİL+VARSAYIM] |
| KKM %90 yüksek tutarlı | | | 90 | TCMB ER 2024-II (haber aktarımı) [İKİNCİL] |

## ANA tablo [HESAP, anahtarlar VEKİL]
| Kanal (anahtar) | Hane | alt | orta | üst |
|---|---|---|---|---|
| TL erimesi (faiz) | −1,12 | −0,08 | −0,16 | −0,88 |
| Kur/DTH (faiz) | +7,58 | +0,52 | +1,10 | +5,96 |
| KKM (faiz) | +3,83 | +0,26 | +0,56 | +3,01 |
| Senyoraj/nakit (tüketim) | −3,93 | −0,85 | −1,61 | −1,47 |
| Banka altını (faiz) | +3,96 | +0,27 | +0,57 | +3,11 |
| **NET (VH hariç)** | **+10,32** | **+0,13** | **+0,45** | **+9,74** |
| Gelir vergisi harcaması (gelir) | +16,20 | +2,71 | +5,79 | +7,71 |
| **NET (VH dahil)** | +26,52 | +2,84 | +6,24 | +17,45 |
| Kâğıt: kiradaki konut (kira) | +26,7 | +1,37 | +6,54 | +18,82 |
| Kâğıt: yastık altı altın 2.200–3.739 t (gelir) [VARSAYIM] | +22,9…+38,9 | +3,8…+6,5 | +8,2…+13,9 | +10,9…+18,5 |

## Ölçütler
- Ö1 (üst payı > gelir payı %47,6): ANA %94 → **TUTTU**. a_KKM90 %99, b_mevduat_dilim %57, d %90; c tanım gereği %47,6 (eşit). Gerçek anahtarlı tüm setlerde tuttu → sağlam [aday].
- Ö2 (alt %40 net < 0, VH hariç): ANA +0,13 → **TUTMADI, sınırda**. a_KKM90 −0,01 (sıfır), b +1,34, c +1,72, d +0,32. Alt grup ne kazandı ne kaybetti; senyoraj kaybı (−0,85) faiz/kur kazançlarını (+1,05) neredeyse sıfırlıyor. VH dahil tüm setlerde alt pozitif (+2,7…+4,4).
- Ö3: Ö1 sağlam, Ö2 anahtara bağlı (−0,01…+1,72).

## Duyarlılık aralığı (NET VH hariç)
alt −0,01…+1,72 | orta +0,16…+3,69 | üst +4,91…+10,17 (üst payı %48–99; gerçek-anahtar setleri %57–99).

## Zayıf noktalar
- Tüm anahtarlar akım (gelir türü) payı; servet (mevduat/altın/konut stoku) beşli dağılımı yok → HFCS benzeri anket bulunamadı. Faiz geliri anahtarı 2018 tek yıl.
- Kaybeden taraf (Hazine −6,9, TCMB, firma) hanelere geri yansıtılmadı: vergi/enflasyon yükünün beşli dağılımı yok. Bu yüzden "alt net ≈0" yalnız hanenin doğrudan pozisyonudur, nihai yük değil.
- Senyoraj: nakit tutmanın beşli dağılımı yok, tüketim payı vekil. Altın: beşli verisi yok.
- Vergi harcaması: hangi istisna kime gidiyor ayrılmadı; gelir payı kaba (asgari ücret istisnası alt-orta lehine, menkul getiri istisnası üst lehine çekerdi).
- KKM içi gerçek/tüzel ve dilim × hesap sayısı tablosu kamuya açık değil (TBMM önergeleri cevapsız).
- Hisse (MKK dilim), ücret payı ayrımı, ev sahibinin oturduğu konut: hesaplanamadı.
- Veri: mevduat dilimleri daha önce EVDS3 keyless web uç noktasından çekilmiş dosyalar; bu tur yeni çağrı yok. Repoya yazılmadı.
