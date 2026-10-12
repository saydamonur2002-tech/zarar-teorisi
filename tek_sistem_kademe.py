"""Tek sistem: mahsup → stok tavan → mevduat adresi, sıralı ve kademeli.

Üç ayrık zaman zarfı (çeyrek); pencereler örtüşmez. Önceki kademe tamamlanınca sonraki başlar.
Pencere içinde uygulama oranı doğrusal kademelenir (1/n .. n/n). Katman sayıları birbirine taşınmaz;
bu dosya yalnızca takvim + etkin oran proxy üretir (senaryo; ölçüm değil).

Çalıştır: python3 tek_sistem_kademe.py
Çıktı: tek_sistem_kademe.csv, tek_sistem_kademe_sonuc.json, TEK_SISTEM_KADEME.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

KOK = Path(__file__).resolve().parent

# Referanslar (depo; koşu anında okunur, başka dosyaya yazılmaz)
AKIS_MAHSUP_ORAN = 0.427  # mahsup_sektor_ozet; baska_nesne, dokunulmaz
FIRMA_MAHSUP_ORAN = 0.32959478056952846  # odeme_mahsup_sonuc ozet brut_azalma_oran
YENI_STOK_TAVAN = 0.2582  # adim1 / bes_adim
ESKI_STOK_TAVAN = 0.0728
MEVDUAT_ADRES_MILYAR = 8322.4 + 4400.1 + 6639.4  # adim4 üç satır
ITIS_YILLIK_MILYAR = 4820.9  # tavan_akis 2025 firma F.4 akımı
F4_STOK_BAS_MILYAR = 25339.8  # tek_sistem_kopru 2026-Q1
BRUT_KIMDEN_KIME_MILYAR = 78870.4  # adim1 TOPLAM brut
# VARSAYIM: yönlendirilen mevduat payının yıllık yeni banka kredi itişinden düşülen oranı (modellenmedi)
K3_MEVDUAT_KREDI_PAYI = 0.08


@dataclass(frozen=True)
class Pencere:
    kademe: int
    kod: str
    ad: str
    katman: str
    baslangic: str  # Donem YYYY-Qn
    bitis: str
    ref_etiket: str
    ref_deger: float
    ref_birim: str


PENCERELER = (
    Pencere(1, "K1_mahsup", "Mahsuplaşma (akış + firma ağı)", "mahsup_sektor_evds.py; odeme_mahsup.py",
            "2027-Q1", "2027-Q4", "sektor_brut_silinen_oran", AKIS_MAHSUP_ORAN, "oran"),
    Pencere(2, "K2_stok", "Stok karşı bacak tavanı", "stok_silim.py; adim1_stok",
            "2028-Q1", "2028-Q4", "yeni_tavan_ust_sinir", YENI_STOK_TAVAN, "oran"),
    Pencere(3, "K3_mevduat", "Mevduat → senet adres yönlendirme", "adim4 (adres adayları)",
            "2029-Q1", "2029-Q4", "adres_mevduat_toplam", MEVDUAT_ADRES_MILYAR, "milyar TL"),
)

DONEM_BAS = "2026-Q4"
DONEM_SON = "2031-Q4"


def _parse_donem(d: str) -> tuple[int, int]:
    y, q = d.split("-Q")
    return int(y), int(q)


def _donem(y: int, q: int) -> str:
    return f"{y}-Q{q}"


def _idx(d: str) -> int:
    y, q = _parse_donem(d)
    return y * 4 + (q - 1)


def _iter_donem(bas: str, son: str) -> list[str]:
    y, q = _parse_donem(bas)
    y2, q2 = _parse_donem(son)
    out = []
    while (y, q) <= (y2, q2):
        out.append(_donem(y, q))
        q += 1
        if q > 4:
            q, y = 1, y + 1
    return out


def _pencere_uzunluk(p: Pencere) -> int:
    return _idx(p.bitis) - _idx(p.baslangic) + 1


def _dogrula_pencereler() -> None:
    ps = sorted(PENCERELER, key=lambda x: x.kademe)
    for i in range(len(ps) - 1):
        if _idx(ps[i].bitis) >= _idx(ps[i + 1].baslangic):
            raise ValueError(f"pencere örtüşmesi: {ps[i].kod} / {ps[i+1].kod}")
    for p in ps:
        if _pencere_uzunluk(p) < 1:
            raise ValueError(f"boş pencere: {p.kod}")


def uygulama_orani(donem: str, p: Pencere) -> float:
    """Pencere içinde kademeli; öncesinde 0; sonrasında 1."""
    i = _idx(donem)
    i0, i1 = _idx(p.baslangic), _idx(p.bitis)
    if i < i0:
        return 0.0
    if i > i1:
        return 1.0
    n = i1 - i0 + 1
    return (i - i0 + 1) / n


def _depo_ref() -> dict:
    out = {"kaynak": "varsayim_sabit"}
    try:
        om = json.loads((KOK / "odeme_mahsup_sonuc.json").read_text(encoding="utf-8"))
        out["firma_mahsup_oran"] = float(om["ozet"]["brut_azalma_oran"])
    except (OSError, KeyError, json.JSONDecodeError):
        out["firma_mahsup_oran"] = FIRMA_MAHSUP_ORAN
    try:
        a1 = json.loads((KOK / "bes_adim_sonuc.json").read_text(encoding="utf-8"))["adimlar"]["1"]
        out["yeni_stok_tavan"] = float(a1["yeni_tavan"])
        out["brut_kimden_kime_milyar"] = float(a1["brut_milyar"])
        out["eski_stok_tavan"] = float(a1["eski_tavan"])
    except (OSError, KeyError, json.JSONDecodeError, TypeError, ValueError):
        out["yeni_stok_tavan"] = YENI_STOK_TAVAN
        out["brut_kimden_kime_milyar"] = BRUT_KIMDEN_KIME_MILYAR
        out["eski_stok_tavan"] = ESKI_STOK_TAVAN
    try:
        import csv as _csv

        ta = next(
            r
            for r in _csv.DictReader((KOK / "tavan_akis.csv").open(encoding="utf-8-sig"))
            if r["yil"] == "2025"
        )
        out["itis_yillik_milyar"] = float(ta["f4_akim"])
    except (StopIteration, OSError, KeyError, ValueError):
        out["itis_yillik_milyar"] = ITIS_YILLIK_MILYAR
    try:
        import csv as _csv

        kop = _csv.DictReader((KOK / "tek_sistem_kopru.csv").open(encoding="utf-8-sig"))
        f4 = next(r for r in kop if r["blok"] == "mutabakat" and r["donem"] == "2026-Q1" and r["evds_anahtar"] == "F_F4_yuk")
        out["f4_stok_bas_milyar"] = float(f4["evds_milyar"])
    except (StopIteration, OSError, KeyError, ValueError):
        out["f4_stok_bas_milyar"] = F4_STOK_BAS_MILYAR
    return out


def _borc_etkisi(u1: float, u2: float, u3: float, depo: dict) -> dict:
    """Kademeli etkin → borç proxy (senaryo; tek defter değil)."""
    sektor = AKIS_MAHSUP_ORAN
    itis = float(depo["itis_yillik_milyar"])
    eski = float(depo.get("eski_stok_tavan") or ESKI_STOK_TAVAN)
    yeni = float(depo["yeni_stok_tavan"])
    brut = float(depo.get("brut_kimden_kime_milyar") or BRUT_KIMDEN_KIME_MILYAR)
    eff_tavan = eski + u2 * (yeni - eski)
    k1_yil = u1 * sektor * itis
    k1_ceyrek = k1_yil / 4
    k2_brut_fazla = u2 * (yeni - eski) * brut
    k3_yon = u3 * MEVDUAT_ADRES_MILYAR
    k3_kredi_yil = k3_yon * K3_MEVDUAT_KREDI_PAYI
    k3_ceyrek = k3_kredi_yil / 4
    baz_ceyrek = itis / 4
    net_yeni = max(0.0, baz_ceyrek - k1_ceyrek - k3_ceyrek)
    return {
        "k1_itis_azalt_milyar_yillik": round(k1_yil, 1),
        "k1_itis_azalt_milyar_ceyrek": round(k1_ceyrek, 1),
        "k2_brut_zincir_fazla_azalt_ust_milyar": round(k2_brut_fazla, 1),
        "k2_etkin_tavan_orani": round(eff_tavan, 4),
        "k3_mevduat_yonlendir_milyar": round(k3_yon, 1),
        "k3_kredi_itki_azalt_milyar_yillik": round(k3_kredi_yil, 1),
        "k3_kredi_itki_azalt_milyar_ceyrek": round(k3_ceyrek, 1),
        "f4_net_yeni_baseline_milyar_ceyrek": round(baz_ceyrek, 1),
        "f4_net_yeni_etkin_milyar_ceyrek": round(net_yeni, 1),
    }


def satirlar_uret() -> list[dict]:
    _dogrula_pencereler()
    depo = _depo_ref()
    sektor_oran = AKIS_MAHSUP_ORAN
    firma_oran = depo["firma_mahsup_oran"]
    stok_tavan = depo["yeni_stok_tavan"]
    f4 = float(depo["f4_stok_bas_milyar"])
    f4_baz = f4
    f4_etkin = f4
    rows = []
    for donem in _iter_donem(DONEM_BAS, DONEM_SON):
        u1 = uygulama_orani(donem, PENCERELER[0])
        u2 = uygulama_orani(donem, PENCERELER[1])
        u3 = uygulama_orani(donem, PENCERELER[2])
        aktif = []
        if u1 > 0:
            aktif.append("K1")
        if u2 > 0:
            aktif.append("K2")
        if u3 > 0:
            aktif.append("K3")
        borc = _borc_etkisi(u1, u2, u3, depo)
        if _idx(donem) >= _idx("2027-Q1"):
            f4_baz += borc["f4_net_yeni_baseline_milyar_ceyrek"]
            f4_etkin += borc["f4_net_yeni_etkin_milyar_ceyrek"]
        rows.append({
            "Donem": donem,
            "K1_uygulama_orani": round(u1, 4),
            "K2_uygulama_orani": round(u2, 4),
            "K3_uygulama_orani": round(u3, 4),
            "etkin_sektor_mahsup_orani": round(u1 * sektor_oran, 4),
            "etkin_firma_mahsup_orani": round(u1 * firma_oran, 4),
            "etkin_stok_tavan_orani": round(u2 * stok_tavan, 4),
            "etkin_mevduat_adres_milyar": round(u3 * MEVDUAT_ADRES_MILYAR, 1),
            **borc,
            "f4_stok_baseline_kumul_milyar": round(f4_baz, 1),
            "f4_stok_etkin_kumul_milyar": round(f4_etkin, 1),
            "f4_stok_fark_milyar": round(f4_baz - f4_etkin, 1),
            "aktif_kademeler": "+".join(aktif) if aktif else "",
            "durum": "senaryo",
        })
    return rows


def md(rows: list[dict], meta: dict) -> str:
    lines = [
        "# Tek sistem — sıralı kademeli üç pencere",
        "",
        "Senaryo takvimi; ölçüm değil. Katman sonuçları birbirine taşınmaz.",
        "",
        f"Çalıştır: `python3 tek_sistem_kademe.py`. Dönem: `{DONEM_BAS}` … `{DONEM_SON}`.",
        "",
        "## Pencereler (ayrık, sıralı)",
        "",
        "| Kademe | Kod | Başlangıç | Bitiş | Katman | Referans |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for p in PENCERELER:
        lines.append(
            f"| {p.kademe} | `{p.kod}` | {p.baslangic} | {p.bitis} | {p.katman} | "
            f"{p.ref_etiket} = {p.ref_deger} {p.ref_birim} |"
        )
    lines += [
        "",
        "Pencere içi: uygulama oranı çeyrekte `1/n … n/n` (doğrusal kademe). Pencere sonrası: **1,0** (açık kalır).",
        "",
        "## Örnek kilometre taşları",
        "",
        "| Dönem | K1 | K2 | K3 | Not |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for d in ("2026-Q4", "2027-Q1", "2027-Q4", "2028-Q1", "2028-Q4", "2029-Q1", "2029-Q4", "2031-Q4"):
        r = next(x for x in rows if x["Donem"] == d)
        note = {
            "2026-Q4": "henüz hiçbiri",
            "2027-Q1": "K1 başlar",
            "2027-Q4": "K1 tam",
            "2028-Q1": "K2 başlar",
            "2028-Q4": "K2 tam",
            "2029-Q1": "K3 başlar",
            "2029-Q4": "üçü tam",
            "2031-Q4": "üçü açık (1,0)",
        }.get(d, "")
        lines.append(
            f"| {d} | {r['K1_uygulama_orani']} | {r['K2_uygulama_orani']} | {r['K3_uygulama_orani']} | {note} |"
        )
    r0 = next(x for x in rows if x["Donem"] == "2026-Q4")
    r27e = next(x for x in rows if x["Donem"] == "2027-Q4")
    r29e = next(x for x in rows if x["Donem"] == "2029-Q4")
    r31e = next(x for x in rows if x["Donem"] == "2031-Q4")
    itis = meta["depo"]["itis_yillik_milyar"]
    lines += [
        "",
        "## Kademeli etkin → borca etkisi (proxy)",
        "",
        "Ölçüm değil; katmanlar birleştirilmedi. **Nominal borç silinmez** (tek sistem kuralı). Etki kanalları:",
        "",
        "| Kademe | Borç nesnesi | Mekanizma | Formül (kademe uygulama u) |",
        "| --- | --- | --- | --- |",
        f"| K1 | Firma **yeni kredi itişi** (F.4 akım proxy) | Brüt mahsup → zinciri çeviren taze akış | `u1 × {AKIS_MAHSUP_ORAN} × itiş_yıllık / 4` çeyrek; itiş={itis} milyar (2025) |",
        "| K1 | **Net stok** | Mahsup net pozisyonu korur | F.4 stokunda **doğrudan düşüş yok**; yalnız itiş freni |",
        f"| K2 | **Kimden-kime brüt stok** (üst sınır) | Karşı bacak tavanı yükselir | `u2 × (yeni−eski) × brüt` = brüt fazlalık azaltılabilir tavan |",
        f"| K3 | **Yeni banka kredi itişi** (varsayım) | Mevduat adresi senede kayar | `u3 × adres × {K3_MEVDUAT_KREDI_PAYI}` / 4 çeyrek; pay VARSAYIM |",
        "",
        "**F.4 stok kumul proxy** (2026-Q1 taban → çeyrek net yeni = itiş/4, 2027-Q1’den itibaren K1+K3 düşülür):",
        "",
        "| Dönem | K1 itiş azalt (milyar/yıl) | K2 brüt üst (milyar) | K3 kredi azalt (milyar/yıl) | F4 baseline | F4 etkin | Fark |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| 2026-Q4 | {r0['k1_itis_azalt_milyar_yillik']} | {r0['k2_brut_zincir_fazla_azalt_ust_milyar']} | {r0['k3_kredi_itki_azalt_milyar_yillik']} | {r0['f4_stok_baseline_kumul_milyar']} | {r0['f4_stok_etkin_kumul_milyar']} | {r0['f4_stok_fark_milyar']} |",
        f"| 2027-Q4 | {r27e['k1_itis_azalt_milyar_yillik']} | {r27e['k2_brut_zincir_fazla_azalt_ust_milyar']} | {r27e['k3_kredi_itki_azalt_milyar_yillik']} | {r27e['f4_stok_baseline_kumul_milyar']} | {r27e['f4_stok_etkin_kumul_milyar']} | {r27e['f4_stok_fark_milyar']} |",
        f"| 2029-Q4 | {r29e['k1_itis_azalt_milyar_yillik']} | {r29e['k2_brut_zincir_fazla_azalt_ust_milyar']} | {r29e['k3_kredi_itki_azalt_milyar_yillik']} | {r29e['f4_stok_baseline_kumul_milyar']} | {r29e['f4_stok_etkin_kumul_milyar']} | {r29e['f4_stok_fark_milyar']} |",
        f"| 2031-Q4 | {r31e['k1_itis_azalt_milyar_yillik']} | {r31e['k2_brut_zincir_fazla_azalt_ust_milyar']} | {r31e['k3_kredi_itki_azalt_milyar_yillik']} | {r31e['f4_stok_baseline_kumul_milyar']} | {r31e['f4_stok_etkin_kumul_milyar']} | {r31e['f4_stok_fark_milyar']} |",
        "",
        f"Tam kademe (2031-Q4): yıllık itiş freni ≈ **{r31e['k1_itis_azalt_milyar_yillik']} milyar TL** "
        f"(≈ %{100 * r31e['k1_itis_azalt_milyar_yillik'] / itis:.1f} itiş); "
        f"K2 brüt üst sınır **{r31e['k2_brut_zincir_fazla_azalt_ust_milyar']} milyar**; "
        f"K3 kredi itişi freni **{r31e['k3_kredi_itki_azalt_milyar_yillik']} milyar/yıl** (varsayım). "
        f"F.4 kumul fark **{r31e['f4_stok_fark_milyar']} milyar** — yalnız itiş proxy; kur/değerleme yok.",
        "",
        "Hane borcu (`uc_kural_senaryo`) bu takvime **bağlı değil**. Çift kayıtta borçlu defteri nominal kalır.",
        "",
        "## Ne denmez",
        "",
        "- “Üçü aynı defterde eşzamanlı entegre edildi” denmez; yalnız takvim.",
        "- “Mevduat dağıtımı modellendi” denmez; K3 etkin adres **milyar TL bandı**, senet `modellenmedi`.",
        "- Stok **silinen** tutarı bu takvimden türetilmez (`silinen` boş).",
        "",
        f"Depo referansı: firma mahsup oranı `{meta['depo'].get('firma_mahsup_oran')}`; "
        f"yeni stok tavan `{meta['depo'].get('yeni_stok_tavan')}`.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = satirlar_uret()
    depo = _depo_ref()
    meta = {
        "donem_bas": DONEM_BAS,
        "donem_son": DONEM_SON,
        "pencereler": [
            {
                "kademe": p.kademe,
                "kod": p.kod,
                "ad": p.ad,
                "baslangic": p.baslangic,
                "bitis": p.bitis,
                "uzunluk_ceyrek": _pencere_uzunluk(p),
                "katman": p.katman,
                "ref_etiket": p.ref_etiket,
                "ref_deger": p.ref_deger,
                "ref_birim": p.ref_birim,
            }
            for p in PENCERELER
        ],
        "depo": depo,
        "kural": "sıralı_pencere; kademeli_rampa; katman_tasinmaz",
        "borc_proxy": {
            "k3_mevduat_kredi_payi_varsayim": K3_MEVDUAT_KREDI_PAYI,
            "f4_net_yeni_formul": "max(0, itis/4 - u1*sektor*itis/4 - u3*adres*pay/4)",
            "k2_f4_stoka_dogrudan_girmez": True,
            "kilometre": {
                d: {
                    "f4_fark_milyar": next(r for r in rows if r["Donem"] == d)["f4_stok_fark_milyar"],
                    "k1_itis_azalt_yillik": next(r for r in rows if r["Donem"] == d)["k1_itis_azalt_milyar_yillik"],
                }
                for d in ("2027-Q4", "2029-Q4", "2031-Q4")
            },
        },
    }
    alan = list(rows[0].keys())
    with (KOK / "tek_sistem_kademe.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        w.writerows(rows)
    (KOK / "tek_sistem_kademe_sonuc.json").write_text(
        json.dumps({"meta": meta, "satir_sayisi": len(rows)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (KOK / "TEK_SISTEM_KADEME.md").write_text(md(rows, meta), encoding="utf-8")
    print("=== tek_sistem_kademe ===")
    for p in PENCERELER:
        print(f"  {p.kod}: {p.baslangic} → {p.bitis} ({_pencere_uzunluk(p)} çeyrek)")
    r29 = next(r for r in rows if r["Donem"] == "2029-Q4")
    print(f"2029-Q4: K1={r29['K1_uygulama_orani']} K2={r29['K2_uygulama_orani']} K3={r29['K3_uygulama_orani']}")


if __name__ == "__main__":
    main()
