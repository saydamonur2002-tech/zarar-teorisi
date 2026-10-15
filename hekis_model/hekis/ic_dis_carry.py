"""Ic / dis carry kanali: firmalarin net doviz acigi artisini kaynagina gore ayirir (2024, 2025).

Carry = faiz - kur artisi (nop_veri.CARRY). Ayrim carry'nin degil, acik artisinin kaynaginindir:
  ic kanal  = yurt ici bankadan doviz kredisi artisi + doviz mevduat varliginin azalmasi (yerlesik TL'ye gecis)
  dis kanal = yurt disi kredi artisi
  diger     = ithalat borcu, ihracat alacagi, turev, FDI, menkul, kalan
Kimlik: acik artisi = yukumluluk artisi - varlik artisi. Seri: TCMB FKDFDVY (data/fkdfdvy_2026_07.json).
n = 2 yil: katsayi degil betimleme; standart hata yok.

Calistir: python -m hekis.ic_dis_carry   (cikti: data/ic_dis_carry.json, IC_DIS_CARRY.md)
"""

import json
import os

from hekis.nop_veri import CARRY, DONEM, S

KOK = os.path.join(os.path.dirname(__file__), "..")
YILLAR = (2024, 2025)


def _d(seri, t):
    i, j = DONEM.index(f"{t}-12"), DONEM.index(f"{t - 1}-12")
    return S[seri][i] - S[seri][j]


def ayir(t):
    ic_kredi, dis_kredi = _d("kredi_ic_banka", t), _d("kredi_yurtdisi", t)
    mev_azalis = -_d("mevduat", t)
    acik = -(S["NOP"][DONEM.index(f"{t}-12")] - S["NOP"][DONEM.index(f"{t - 1}-12")])
    ic, dis = ic_kredi + mev_azalis, dis_kredi
    diger = acik - ic - dis
    c = CARRY[t]
    return {
        "yil": t, "carry_puan": round(c, 1), "acik_artisi": round(acik, 1),
        "ic_kredi": round(ic_kredi, 1), "ic_mevduat_azalis": round(mev_azalis, 1), "ic_kanal": round(ic, 1),
        "dis_kanal": round(dis, 1), "diger": round(diger, 1),
        "ic_pay": round(ic / acik, 2), "dis_pay": round(dis / acik, 2),
        "ic_per_puan": round(ic / c, 2), "dis_per_puan": round(dis / c, 2),
    }


def main():
    r = [ayir(t) for t in YILLAR]
    json.dump(r, open(os.path.join(KOK, "data", "ic_dis_carry.json"), "w"), indent=1, ensure_ascii=False)
    L = ["# Ic ve dis carry kanali (2024, 2025)", "",
         "Carry = faiz - kur artisi. Acik artisi = yukumluluk artisi - varlik artisi (FKDFDVY, mlr $). Ic kanal = yurt ici banka doviz kredisi artisi + doviz mevduat azalisi; dis kanal = yurt disi kredi artisi. n=2 yil: betimleme, katsayi degil.", "",
         "| Yil | Carry (puan) | Acik artisi | Ic kanal | (kredi + mevduat azalisi) | Dis kanal | Diger | Ic pay | Dis pay | Ic / carry puani | Dis / carry puani |",
         "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for x in r:
        L.append(f"| {x['yil']} | {x['carry_puan']} | {x['acik_artisi']} | {x['ic_kanal']} | {x['ic_kredi']} + {x['ic_mevduat_azalis']} | {x['dis_kanal']} | {x['diger']} | {x['ic_pay']} | {x['dis_pay']} | {x['ic_per_puan']} | {x['dis_per_puan']} |")
    L += ["", "## Ne denmez", "",
          "- Iki yildan carry katsayisi cikmaz; ic ve dis kanalin carry'e duyarliligi tahmin degil, iki gozlemin oranidir.",
          "- Mevduat azalisi carry'e bagli TL'ye gecis denmez: mevduat kullanimi, borc odeme ve kur korumali hesaplar da azaltir (dipnot: yurt ici mevduat kur korumali hesaplari icerir).",
          "- 'Diger' kalemi ithalat borcu, ihracat alacagi, turev, FDI ve menkulu birlikte tasir; ayristirilmadi.",
          "- Faiz serisi (nop_veri.FAIZ) Drive V22'den elle girilmistir; hangi faiz oldugu belirtilmemistir."]
    open(os.path.join(KOK, "IC_DIS_CARRY.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
