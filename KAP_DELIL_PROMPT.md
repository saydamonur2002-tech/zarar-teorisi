# KAP delil algoritması

KAP bildirimlerini tara. Amaç: büyük tüzel yapıların nakit/mevduat, ödeme gecikmesi, FX pozisyonu ve ilgili özel durum açıklamalarında delil aramak.

## Girdi

- KAP özel durum açıklamaları ve finansal dipnotlar (nakit ve nakit benzeri, finansal borçlar, döviz pozisyonu).
- Hedef: BIST 100 + büyük özel (mümkünse) şirketler, son 4 yıl (2022–2026).
- Odak kalemler: nakit ve mevduat, kısa vadeli finansal borç, döviz yükümlülüğü, ödeme gecikmesi / konkordato / temerrüt, ilişkili taraf alacak-borç.

## Delil algoritması (kural)

1. Nakit yoğunluğu: nakit+mevduat / toplam varlık > eşik (0,15) ve aynı dönemde kısa vadeli borç servisi gecikmiş veya yeniden yapılandırılmış.
2. FX uyumsuzluğu: döviz yükümlülüğü payı yüksek, döviz varlığı düşük, aynı dönemde kur şoku sonrası özel durum.
3. Ödeme gecikmesi işareti: “gecikme”, “temerrüt”, “konkordato”, “ödeme planı”, “alacak devri”, “faktoring” geçen özel durumlar.
4. İlişkili taraf: grup içi alacak-borç bakiyesi büyük ve net pozisyon tek yönlü.
5. Zaman yakınlığı: yukarıdaki işaretlerin 90 gün içinde birden fazla şirkette tekrarlanması.

## Çıktı

- Şirket × yıl: nakit/varlık, kısa borç/nakit, FX açık, delil skoru (0–5).
- Delil skoru ≥ 3 olanları listele (tarih, bildirim linki, kısa alıntı).
- Sektör ve büyüklük kırılımı.
- “En yüksek nakit” sıralaması (lider adayları). İsimli, ölçülmüş, eksik olabilir — eksikliği belirt.

## Sınır

- Sadece KAP’ta yayımlanmış metin ve tablolar. Varsayım yok.
- Özel şirketler yoksa “yok” de.
- Skor model katsayısı değil; tarama indeksi.

Tekrarlanabilir dosya ve kısa özet üret.
