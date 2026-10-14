# Rakip ikame akışı çift sayımı: doğrulama

Ana model değiştirilmedi. Aynı v hem havza girişine hem aktör ikame kazancına yazılıyor; korunum (V) aşılıyor. Hangi tarafın düşüleceği karar gerektirir.

| Senaryo | Kenar toplamı | Havza girişi (ig) | Aktör ikame kazancı | V | Aktör kazancı | Aktör + ig | V aşımı |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 5.418 | 5.412 | 4.414 | 25.397 | 25.396 | 30.808 | **5.411** |
| B | 8.61 | 8.621 | 5.419 | 40.462 | 40.462 | 49.083 | **8.621** |
| C | 3.717 | 3.711 | 3.384 | 17.398 | 17.048 | 20.759 | **3.361** |

## Düzeltme varyantlarının etkisi

| Senaryo | Ölü ağırlık | K1: aktör ikame düşülürse | K2: havza girişi düşülürse | Σ net (mevcut / K1 / K2) |
| --- | ---: | ---: | ---: | --- |
| A | 14.802 | 19.216 | 20.214 | -44.94 / -49.355 / -50.086 |
| B | 25.43 | 30.849 | 34.051 | -77.937 / -83.358 / -86.128 |
| C | 10.022 | 13.406 | 13.733 | -29.773 / -33.158 / -33.303 |

## Sınıf değişimi (mevcut → K1 → K2)

- **A:** CY: bant_ici → bant_ici → kaybeden; EG: bant_ici → kaybeden → kaybeden; SA: kazanan → bant_ici → kazanan
- **B:** EG: bant_ici → kaybeden → kaybeden; SA: kazanan → bant_ici → kazanan
- **C:** CY: bant_ici → bant_ici → kaybeden; EG: bant_ici → kaybeden → kaybeden; GR: bant_ici → kaybeden → bant_ici; US: kazanan → bant_ici → kazanan

Aynı ülkenin hem havza girişi hem aktör ikame kazancı olduğu durumlar: A: AL, BA, BG, EG, IL, IR, MK, RS; B: AL, BA, BG, EG, IL, IR, MK, RS; C: AL, BA, BG, EG, IL, IR, MK, RS
