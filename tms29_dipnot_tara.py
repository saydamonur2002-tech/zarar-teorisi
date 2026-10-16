"""2022 ve 2023 dipnot metninde enflasyon dışı düzeltme ibaresini tarar.

OCI 'yeniden sınıflandırılacak' eşleşmeleri satış düzeltmesi sayılmaz.
Çıktı, ibarenin geçtiği kısa penceredir; neden çıkarımı bu dosyada yoktur.
"""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

KODLAR = (
    "AKSA ARSAN ATEKS BAYRK BLCYT BOSSA BRKO BRMEN DAGI DERHL DERIM DESA "
    "DIRIT ENSRI HATEK ISSEN KORDS KRTEK LUKSK MAVI MEGAP MNDRS RALYH RODRG "
    "RUBNS SASA SKTAS SNPAM SONME SUNTK SUWEN YUNSA"
).split()
PDF = Path("/tmp/kap_tms29_pdf")
PDF.mkdir(exist_ok=True)
CACHE = Path("/tmp/kap_xbrl_satir")


def indir(kod, idx, obj):
    txt = PDF / f"{kod}_{idx}.txt"
    if txt.exists() and txt.stat().st_size > 200:
        return kod, idx, "onbellek", txt.stat().st_size
    url = f"https://www.kap.org.tr/tr/api/file/download/{obj}"
    son_hata = "bilinmiyor"
    for deneme in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": f"https://www.kap.org.tr/tr/Bildirim/{idx}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            break
        except Exception as exc:  # noqa: BLE001
            son_hata = str(exc)
            raw = b""
    if not raw:
        return kod, idx, "indirme:" + son_hata[:80], 0
    i = raw.find(b"%PDF")
    if i < 0:
        return kod, idx, "pdf_degil", 0
    path = PDF / f"{kod}_{idx}.pdf"
    path.write_bytes(raw[i:])
    subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), str(txt)], check=False, timeout=90)
    if not txt.exists():
        return kod, idx, "pdftotext_yok", 0
    return kod, idx, "ok", txt.stat().st_size


def pencereler(metin, desen, n=220):
    out = []
    for m in re.finditer(desen, metin, re.I):
        a = max(0, m.start() - 80)
        b = min(len(metin), m.end() + n)
        parca = re.sub(r"\s+", " ", metin[a:b]).strip()
        out.append(parca)
        if len(out) >= 8:
            break
    return out


DESEN = {
    "tms29": r"TMS\s*29",
    "satin_alma": r"satın alma gücü",
    "enflasyon_duzeltme": r"enflasyon düzeltmesi",
    "yeniden_sinif": r"yeniden sınıfland\w+",
    "hata_duzeltme": r"hata(?:lar)?ın düzeltilmesi|geçmiş yıllar kar|önceki dönem(?:e ait)? .*düzelt",
    "hasilat_duzeltme": r"hasılat.{0,80}yeniden|satış hasılatı.{0,80}düzelt",
}


def sinifla(parca):
    u = parca.lower()
    if "yeniden sınıflandırılacak" in u or "yeniden sınıflandırılmayacak" in u:
        return "oci"
    if "gerekli görüldüğünde yeniden sınıflandır" in u:
        return "politika_sablonu"
    return "diger"


def tara(yol):
    if not yol.exists() or yol.stat().st_size < 200:
        return {"durum": "metin_yok", "boy": yol.stat().st_size if yol.exists() else 0}
    metin = yol.read_text(encoding="utf-8", errors="replace")
    hits = {}
    for ad, desen in DESEN.items():
        p = pencereler(metin, desen)
        if ad == "yeniden_sinif":
            p = [{"sinif": sinifla(x), "metin": x} for x in p]
        hits[ad] = p
    return {"durum": "ok", "boy": len(metin), "hits": hits}


def main():
    isler = []
    for kod in KODLAR:
        y23 = json.loads(Path(f"/tmp/kap_tms29/{kod}.json").read_text(encoding="utf-8"))
        for b in y23["bildirimler"]:
            rec = json.loads((CACHE / f"{b['idx']}.json").read_text(encoding="utf-8"))
            if not rec.get("pdf_obj"):
                print("pdf_obj yok", kod, b["idx"])
                continue
            isler.append((kod, b["idx"], rec["pdf_obj"]))
    print("pdf", len(isler), flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(indir, *x) for x in isler]
        for n, fut in enumerate(as_completed(futs), 1):
            kod, idx, durum, boy = fut.result()
            print(f"{n}/{len(isler)} {kod} {idx} {durum} {boy}", flush=True)
    ozet = {"2022": {}, "2023": {}}
    for kod in KODLAR:
        ozet["2022"][kod] = tara(Path(f"/tmp/kap_tekstil/{kod}_2022.txt"))
        y23 = json.loads(Path(f"/tmp/kap_tms29/{kod}.json").read_text(encoding="utf-8"))
        ozet["2023"][kod] = []
        for b in y23["bildirimler"]:
            ozet["2023"][kod].append({"idx": b["idx"], "tarih": b.get("tarih"), **tara(PDF / f"{kod}_{b['idx']}.txt")})
    Path("/tmp/tms29_dipnot.json").write_text(json.dumps(ozet, ensure_ascii=False), encoding="utf-8")
    for kod in KODLAR:
        for bl in ozet["2023"][kod]:
            if bl.get("durum") != "ok":
                print("2023 metin yok", kod, bl.get("idx"), bl.get("durum"), bl.get("boy"))
                continue
            diger = [x for x in bl["hits"]["yeniden_sinif"] if x["sinif"] == "diger"]
            print(kod, bl["idx"], "tms29", len(bl["hits"]["tms29"]), "diger_sinif", len(diger), "hasilat", len(bl["hits"]["hasilat_duzeltme"]))


if __name__ == "__main__":
    main()
