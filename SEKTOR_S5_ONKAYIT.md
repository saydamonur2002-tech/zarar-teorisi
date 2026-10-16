# Ön kayıt — S5 kayıp aktarımı

Yazıldı: 2026-10-16, seri değerleri çekilmeden. `SEKTOR_DOVIZ_ONKAYIT.md` içindeki S5 tanımı durur. Eşikler değişmez.

## Ölçüldü sayılma

S5 ölçüldü denir, ancak aynı NACE kesiminde ikisi de varsa: özkaynağı aşan döviz kaybı, ve bu kaybın o kesimin banka kredisine ya da o kesime yazılmış bir TCMB döviz satışına geçtiği gözlem. Kesim etiketi yoksa toplam stokun artması aktarım sayılmaz. Sonuç belirlenemiyor kalır.

Kesim döviz kaybı `SEKTOR_DOVIZ_POZISYON.md` içinde yazılmadı. Bu tur onu türetmez.

## Kilitli seriler

Banka kanalı, stok, karar serisi: `TP.HPBITABLO6.26`. Grup `bie_hpbitablo6`. Ad: 1.2.1.b.YP. Üst satır 1.2.1 ticari krediler, finansal kesim dışı kuruluşlar. Haftalık. Toplulaştırma last. NACE kırılımı değildir.

Aynı tabloda duran ve toplanmayan satırlar: `TP.HPBITABLO6.32` (1.2.2.b.YP, diğer krediler), `TP.HPBITABLO6.35` (1.2.3.b.YP, kurumsal kredi kartı). Takipteki alacak aktarım yerine konmaz.

Firma tarafı, stok, NACE değil: `TP.FDVY16`. Grup `bie_fdvy`. Ad: B.a.1.1.1.Döviz Kredileri, yurt içi bankalar. Aylık. Toplulaştırma last. `TP.FDVY19` dövize endeksli kredidir, döviz kredisine eklenmez.

Çekilmeyecekler: `TP.FDVY02` ile `TP.FDVY04` mevduattır. `TP.FDVY37` net döviz pozisyonudur ve varlık tarafında mevduat taşır. Altın ve mevduat beklemede. Net pozisyon hesaba girmez.

TCMB satışı, akım: `TP.SATIM.USD`, `TP.SATIM.EUR`, `TP.SATIM.CHF`, `TP.SATIM.DEM`. Grup `bie_dovefmud`, arşiv, doğrudan müdahale. Para birimleri toplanmaz ve kurla çevrilmez. Boş gün sıfır yazılmaz. `TP.DF.*` piyasa hacmi satış yerine konmaz. Alım serileri karar serisi değildir.

## Katsayı

Regresyon yazılmaz. Gözlem sayısı raporlanır. Otuz altı gözlem eşiği bir katsayı içindir. Katsayı olmadığı için eşik bir kanal kararı üretmez.
