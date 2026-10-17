"""Kapanış: beş iş, tek test.

Okur, yazmaz (iki sonuç dosyası dışında). Beş kontrol:
  1. tek_sistem_esleme.csv adım 1 stok satırı iki değer taşır (eski_tavan, yeni_tavan), etiket `ust_sinir`, tek sayı yok.
  2. Silinen boş: adim1_stok.csv her satır, eşleme satırı.
  3. Senet kilidi: senet_kilit.txt `modellenmedi`; adim4.csv senet satırı `modellenmedi`, ihraç/prim/çıkış boş; kod yok.
  4. Üç kapı boş: kapi_kilit.txt üç satır `bos`; tavan_akis.csv gecis/tavan, vadeli_kalicilik.csv vade/emir/gün boş.
  5. Akış satırı 0,4270 `baska_nesne` durur.
Beşi geçerse `bitti`, biri düşerse `durdu`. bes_adim_sonuc.json `son` bu testten yazılır; koşunun sözü (`kosu`) ayrı durur.

Çalıştır: `python3 test_bes_adim.py` (pytest de toplar). Çıktı: kapanis_sonuc.json; bes_adim_sonuc.json `son`, `son_kaynak`.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent
def _eski_tavan() -> float:
    """stok_silim_sonuc.json'dan her koşuda okunur (eski: sabit 0.0728)."""
    import json as _j
    from pathlib import Path as _P
    d = _j.loads((_P(__file__).resolve().parent / "stok_silim_sonuc.json").read_text(encoding="utf-8"))
    def _bul(o):
        if isinstance(o, dict):
            if "arac_ayri_oran_ust_sinir" in o: return o["arac_ayri_oran_ust_sinir"]
            for v in o.values():
                r = _bul(v)
                if r is not None: return r
        return None
    return float(_bul(d))


ESKI_TAVAN = _eski_tavan()
AKIS = (0.427, "baska_nesne")
KAPILAR = ("vade_dilimi", "odenmeyen_emir", "gecis_payi")
KOD_HARIC = ("hekis_model", "model", "mahsup", ".git")  # vendor; HEKİS senedi başka nesne


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def _bos(x) -> bool:
    return x is None or str(x).strip() == ""


def _f(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _stok_satiri() -> dict | None:
    return next((r for r in _csv("tek_sistem_esleme.csv") if r["adim"] == "1" and "stok_silim.py" in r["katman"]), None)


def kontrol_esleme() -> dict:
    r = _stok_satiri()
    if r is None:
        return {"etiket": "ihlal", "not": "stok satırı bulunamadı"}
    toplam = next((x for x in _csv("adim1_stok.csv") if x["cift"] == "TOPLAM"), {})
    eski, yeni = _f(r.get("eski_tavan")), _f(r.get("yeni_tavan"))
    iki_deger = eski is not None and yeni is not None and _bos(r.get("deger"))
    eski_ok = eski is not None and abs(eski - ESKI_TAVAN) < 5e-5
    yeni_ok = yeni is not None and _f(toplam.get("yeni_tavan")) is not None and abs(yeni - _f(toplam["yeni_tavan"])) < 5e-5
    ust = r["durum"] == "ust_sinir"
    ok = iki_deger and eski_ok and yeni_ok and ust
    return {"etiket": "temiz" if ok else "ihlal", "eski_tavan": eski, "yeni_tavan": yeni, "durum": r["durum"],
            "not": "iki değer, ust_sinir" if ok else f"iki_deger {iki_deger}, eski_ok {eski_ok}, yeni_ok {yeni_ok}, durum {r['durum']}"}


def kontrol_silinen() -> dict:
    a1 = _csv("adim1_stok.csv")
    r = _stok_satiri() or {}
    dolu = [x["cift"] for x in a1 if not _bos(x.get("silinen"))]
    esl_bos = _bos(r.get("silinen")) and "Silinen boş" in r.get("not", "")
    ok = not dolu and esl_bos and (KOK / "adim1_stok.csv").exists()
    return {"etiket": "temiz" if ok else "ihlal", "adim1_dolu_satir": dolu, "esleme_silinen_bos": esl_bos,
            "not": "silinen boş; xls yok" if ok else "silinen dolu"}


def kontrol_senet() -> dict:
    kilit = (KOK / "senet_kilit.txt").read_text(encoding="utf-8").strip() if (KOK / "senet_kilit.txt").exists() else None
    senet = next((x for x in _csv("adim4.csv") if "senet" in x["nesne"]), None)
    satir_ok = senet is not None and senet["durum"] == "modellenmedi" and all(_bos(senet.get(k)) for k in ("ihrac", "prim", "cikis", "deger"))
    kod: list[str] = []
    for p in KOK.rglob("*.py"):
        rel = p.relative_to(KOK)
        if rel.parts[0] in KOD_HARIC or p.name == Path(__file__).name:
            continue
        if "senet" in p.name.lower():
            kod.append(str(rel)); continue
        if re.search(r"^\s*(def|class)\s+\w*senet\w*", p.read_text(encoding="utf-8", errors="ignore"), re.I | re.M):
            kod.append(str(rel))
    ok = kilit == "modellenmedi" and satir_ok and not kod
    return {"etiket": "temiz" if ok else "ihlal", "kilit": kilit, "satir": senet["durum"] if senet else None, "kod": kod,
            "not": "kilit duruyor; satır modellenmedi; kod yok" if ok else "kilit değişmiş, satır dolu veya kod var"}


def kontrol_kapilar() -> dict:
    satirlar = [l.split() for l in (KOK / "kapi_kilit.txt").read_text(encoding="utf-8").splitlines() if l.strip()] \
        if (KOK / "kapi_kilit.txt").exists() else []
    kilit = {l[0]: l[-1] for l in satirlar if len(l) >= 2}
    kilit_ok = len(satirlar) == 3 and all(kilit.get(k) == "bos" for k in KAPILAR)
    ta, vk = _csv("tavan_akis.csv"), _csv("vadeli_kalicilik.csv")
    veri = {"gecis_payi": all(_bos(r["gecis"]) and _bos(r["tavan"]) for r in ta),
            "vade_dilimi": all(r["vade_kirilim"] == "ayrılmadı" and _bos(r["ortalama_gun"]) for r in vk),
            "odenmeyen_emir": all(_bos(r["odenmeyen_emir_milyar"]) for r in vk)}
    ok = kilit_ok and all(veri.values())
    return {"etiket": "temiz" if ok else "ihlal", "kilit": kilit, "veri_bos": veri,
            "not": "üçü boş; varsayim_esik.csv eşikleri taşınmadı" if ok else "kilit bozuk veya kapı dolu"}


def kontrol_akis() -> dict:
    r = next((x for x in _csv("tek_sistem_esleme.csv") if x["adim"] == "1" and x["dosya"] == "mahsup_sektor_ozet.json"), None)
    ok = r is not None and _f(r["deger"]) is not None and abs(_f(r["deger"]) - AKIS[0]) < 5e-5 and r["durum"] == AKIS[1]
    return {"etiket": "temiz" if ok else "ihlal", "deger": _f(r["deger"]) if r else None, "durum": r["durum"] if r else None,
            "not": "0,4270 baska_nesne durur" if ok else "akış satırı değişmiş"}


def main() -> dict:
    kontrol = {"esleme_iki_deger": kontrol_esleme(), "silinen_bos": kontrol_silinen(), "senet_kilit": kontrol_senet(),
               "uc_kapi_bos": kontrol_kapilar(), "akis_satiri": kontrol_akis()}
    son = "bitti" if all(k["etiket"] == "temiz" for k in kontrol.values()) else "durdu"

    ba_yol = KOK / "bes_adim_sonuc.json"
    ba = json.loads(ba_yol.read_text(encoding="utf-8")) if ba_yol.exists() else {}
    ba["son"] = son
    ba["son_kaynak"] = "test_bes_adim.py"
    ba["test_kontrol"] = {k: v["etiket"] for k, v in kontrol.items()}
    ba_yol.write_text(json.dumps(ba, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    geri = json.loads(ba_yol.read_text(encoding="utf-8"))
    ht = "temiz" if (geri.get("son") == son and geri.get("son_kaynak") == "test_bes_adim.py" and son == "bitti") else "ihlal"

    isler = {
        "is1_esleme": {"H-K1": kontrol["esleme_iki_deger"]["etiket"], **kontrol["esleme_iki_deger"]},
        "is2_silinen": {"H-K2": kontrol["silinen_bos"]["etiket"], **kontrol["silinen_bos"]},
        "is3_senet": {"H-K3": kontrol["senet_kilit"]["etiket"], **kontrol["senet_kilit"]},
        "is4_kapilar": {"H-K4": kontrol["uc_kapi_bos"]["etiket"], **kontrol["uc_kapi_bos"]},
        "is5_test": {"H-T": ht, "etiket": ht, "akis_satiri": kontrol["akis_satiri"]["etiket"],
                     "not": "test var; son satır testten" if ht == "temiz" else "test düştü veya son satır testten değil"},
    }
    kap = {"on_kayit": "c24fb00", "kosu_sozu": ba.get("kosu"), "isler": isler, "son": son, "kaynak": "test_bes_adim.py",
           "not": "Tavan 0,2582 üst sınır; silinen boş. Koşunun sözü ile testin sözü ayrı."}
    (KOK / "kapanis_sonuc.json").write_text(json.dumps(kap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for ad, v in isler.items():
        print(f"{ad:<12} {v['etiket']}  {v['not']}")
    print("son:", son, "| kaynak: test_bes_adim.py | koşunun sözü:", ba.get("kosu"))
    return kap


def test_kapanis() -> None:
    kap = main()
    assert kap["son"] == "bitti", kap["isler"]


if __name__ == "__main__":
    main()
