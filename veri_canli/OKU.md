# Canlı EVDS verisi

Bu klasörü `haftalik_guncelle.py` yazar; elle düzenlemeyin. Özet her çalışmadan sonra kökteki `SON_GUNCELLEME.md` dosyasında, kısa geçmiş `GUNLUK.md` içindedir (ikisi de ilk değişiklikte oluşur).

| | Dondurulmuş `*_ham.csv` (kök) | Canlı `veri_canli/*.csv` |
| --- | --- | --- |
| Çekim | 7 Ekim 2026, tek seferlik | haftalık; değişiklik yoksa dosya yazılmaz |
| Kullanan | modelin tüm betikleri ve testleri | yalnızca takip; model buradan okumaz |
| Bitiş tarihi | 07-10-2026 | çalışma günü |

Model çıktıları (L/G matrisleri, skorlar, `*_ozeti.json`) bu veriyle **yeniden hesaplanmaz**.

## Kapsam

Sekiz dosya, 37 EVDS grubu: `akim_ve_tcmb`, `butce`, `dis_borc`, `faiz`, `mahsup_evds`, `npl`, `prov`, `s125`. Grup listesi ve her grubun başlangıç tarihi `kaynaklar.json` içindedir; başlangıç, dondurulmuş dosyada o grubun ilk dönemidir. Her grup `freq="5"` ile çekilir (`evds_cek.py` varsayılanı). Kök dizindeki diğer `*_ham.csv` dosyaları özel sorgularla veya elle üretildiği için kapsam dışıdır.

## Bilinmesi gerekenler

- **Çeyreklik finansal hesaplar** TCMB tarafından çeyrekte bir ve gecikmeli yayımlanır; çoğu hafta bu dosyalarda değişiklik çıkmaz. Aylık seriler (bütçe, faiz, NPL) ve dış borç daha sık güncellenir.
- **Açık dönem:** Serinin en son dönemi (ay veya çeyrek) tamamlanana kadar haftadan haftaya değişebilir. Özette ayrı sayılır ve revizyon sayılmaz.
- **Koruma:** Yeni çekim eski satır sayısının %80'inden azsa dosya yazılmaz ve iş hata verir; boş yanıt da hatadır. Hata durumunda GitHub size e-posta atar.

## Doğrulama durumu

Birim testleri geçiyor (`test_haftalik_guncelle.py`). Dondurulmuş dosyalarla **gerçek EVDS karşılaştırması henüz yapılmadı.** İlk çalışmada özet 7 Ekim tabanına göre farkı gösterir. Aylık dosyalarda (`faiz`, `npl`, `prov`) çok sayıda "yeni gözlem" ve "silinen" görürseniz sıklık parametresi yanlış demektir; önce ona bakın.
