# Tek sistem

Borç akışla ödenir, servet üretime bağlanır.

İki öneri tek sistemdir. 3 Ekim parçası kilitli lira alacağını açar. 4 Ekim parçası açılan paranın adresini söyler. Silme yok. Tasfiye yok.

Tam metin: [RAPOR.md](RAPOR.md)

Mahsup modeli (adım 1-3, çalışan kod): [mahsup/](mahsup/)

## Beş adım

1. Lira alacak ve borç e-fatura üzerinden eşleşir. Kapalı döngü nakit dolaşmadan kapanır.
2. Kalan net borç silinmez. Üstten alta akış planıyla ödenir. Alta inen pay ücret olarak yazılır.
3. Bu akış yeni banka kredisiyle çevrilmez. Eski stokun faizi, stok ödenene kadar durur.
4. Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider. Çıkış, senedi başkasına satmaktır.
5. Konut topluma açılırsa kira, aynı akışın ikinci koludur. Bu kol ölçülmedi.

## Sınır

Kart borcunu, döviz sözleşmesini ve Hazine faizini kapatmaz. Enflasyonda tavan birkaç puandır. 20 vaadi verilmez.
