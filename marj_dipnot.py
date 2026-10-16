"""KAP yıllık finansal rapor dipnotundan finansman gelir/gider kırılımı.

Yüz XBRL toplamı kontrol kabul edilir. Dipnot satırları toplamı bu toplama
kapanmazsa firma-yıl ayrıştırılmış sayılmaz.
"""
from __future__ import annotations

import re

NUM = re.compile(
    r"\(\s*\d{1,3}(?:\.\d{3})+(?:,\d+)?\s*\)|\(\s*\d+(?:,\d+)?\s*\)|(?<![\d.])\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\d.])"
)


def tr_num(tok: str) -> float | None:
    t = tok.strip().replace(" ", "")
    neg = t.startswith("(") and t.endswith(")")
    if neg:
        t = t[1:-1]
    if t.count(",") == 1 and "." in t:
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(".", "")
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


TOKEN = re.compile(
    r"\(\s*\d{1,3}(?:\.\d{3})+(?:,\d+)?\s*\)|\(\s*\d+(?:,\d+)?\s*\)|(?<![\d.])\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\d.])|(?<![\d.])\d{1,6}(?![\d.])"
)


_AY = r"ocak|şubat|subat|mart|nisan|mayıs|mayis|haziran|temmuz|ağustos|agustos|eylül|eylul|ekim|kasım|kasim|aralık|aralik"


def satir_sayilari(line: str) -> list[float]:
    temiz = re.sub(rf"\b\d{{1,2}}\s+(?:{_AY})\s+\d{{4}}\b", " ", line, flags=re.I)
    temiz = re.sub(r"\(\d{1,2}\)", " ", temiz)  # dipnot işareti, tutar değil
    temiz = re.sub(r"(?<=\s)--(?=\s|$)", " 0 ", temiz)
    temiz = re.sub(r"(?<=\s)-(?=\s|$)", " 0 ", temiz)
    temiz = re.sub(r"\(Not\s*\d+\)", " ", temiz, flags=re.I)
    temiz = re.sub(r"\bNot\s+\d+\b", " ", temiz, flags=re.I)
    out = []
    for m in TOKEN.finditer(temiz):
        raw = m.group(0)
        v = tr_num(raw)
        if v is None:
            continue
        if 1990 <= abs(v) <= 2035 and "." not in raw and "(" not in raw:
            continue
        out.append(v)
    return out


def _tarih_satiri(line: str) -> bool:
    u = line.lower()
    if not any(k in u for k in ("ocak", "aralık", "aralik", "şubat", "subat", "mart", "nisan", "mayıs", "mayis", "haziran", "temmuz", "ağustos", "agustos", "eylül", "eylul", "ekim", "kasım", "kasim")):
        return False
    kalan = re.sub(r"[\d\s\-\./]+", "", u)
    kalan = re.sub(r"ocak|aralık|aralik|şubat|subat|mart|nisan|mayıs|mayis|haziran|temmuz|ağustos|agustos|eylül|eylul|ekim|kasım|kasim", "", kalan)
    return len(kalan) <= 2


def birlestir(lines: list[str]) -> list[str]:
    out: list[str] = []
    buf = ""
    for raw in lines:
        line = raw.strip()
        if not line or _tarih_satiri(line) or re.fullmatch(r"[\d\s]{4,12}", line):
            continue
        if satir_sayilari(line):
            out.append((buf + " " + line).strip() if buf else line)
            buf = ""
        else:
            buf = (buf + " " + line).strip()
    if buf:
        out.append(buf)
    return out


def sinif(label: str) -> str:
    u = label.lower().replace("ı", "i").replace("İ", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")
    if "kur fark" in u or "kambiyo" in u:
        return "kur"
    if any(k in u for k in ("faiz", "katilim", "kar payi", "reeskont", "iskonto")):
        return "faiz"
    if "kiralama" in u and "finansman" in u:
        return "faiz"
    return "diger"


def _baslik(line: str, taraf: str) -> bool:
    # Dipnot numarası ("28 Finansman gelirleri", "DİPNOT 23 - ...") tutar değildir.
    # İ harfi, küçük harf eşlemesinde 'dipnot' kalıbını kaçırır.
    line = line.strip().replace("İ", "I").replace("ı", "i")
    line = re.sub(r"^\s*(?:DIPNOT|NOT)?\s*\d{1,2}\s*[-–.]?\s*", "", line, flags=re.I)
    if satir_sayilari(line):
        return False
    u = line.lower()
    if "toplam" in u or "öncesi" in u or "oncesi" in u:
        return False
    # Dipnot cümlesi başlık değildir ("...finansman giderlerinden oluşmaktadır").
    if len(line) > 90 or "olus" in u or "oluş" in u:
        return False
    if taraf == "gelir":
        return "finansman gelir" in u or "finansal gelir" in u
    return "finansman gider" in u or "finansal gider" in u or ("finansman" in u and "gider" in u)


def blok_ayir(metin: str, hedef: float, taraf: str) -> dict:
    """hedef: yüzdeki finansman tutarı, sunum biriminde.

    taraf 'gelir' veya 'gider'. Gider dipnotu çoğu zaman pozitif yazılır;
    hedef mutlak değeriyle aranır. Başlık ile toplam satırı arasındaki
    kalemler toplanır. Toplam, hedefe yüzde 1 içinde kapanmazsa durum
    'kapanmadi' olur ve medyana alınmaz.
    """
    hedef_abs = abs(hedef)
    if hedef_abs == 0:
        return {"durum": "sifir", "kur": 0.0, "faiz": 0.0, "diger": 0.0, "toplam": 0.0, "satir": []}
    lines = metin.splitlines()
    aday = []
    for i, line in enumerate(lines):
        nums = satir_sayilari(line)
        if nums and any(abs(abs(n) - hedef_abs) <= max(1.0, hedef_abs * 0.005) for n in nums):
            aday.append(i)
    if not aday:
        return {"durum": "toplam_satiri_yok", "satir": []}
    best = None
    for i in aday:
        bas = None
        for j in range(i - 1, max(-1, i - 80), -1):
            if _baslik(lines[j], taraf):
                bas = j
                break
        if bas is None:
            continue
        pencere = lines[bas + 1: i]
        # karşı tarafın başlığına gelindiyse kes
        kes = []
        for line in pencere:
            if _baslik(line, "gider" if taraf == "gelir" else "gelir"):
                break
            kes.append(line)
        pencereler = [kes]
        son_toplam = None
        for n, line in enumerate(kes):
            if "toplam" in line.lower() and satir_sayilari(line):
                son_toplam = n
        if son_toplam is not None and son_toplam + 1 < len(kes):
            # Aynı başlık altında gider ve gelir art arda ise, ara toplamdan sonrası ayrı bloktur.
            pencereler.append(kes[son_toplam + 1:])
        for pencere_kalem in pencereler:
            bir = birlestir(pencere_kalem)
            kalem = []
            for line in bir:
                nums = satir_sayilari(line)
                if not nums:
                    continue
                cari = nums[0]
                et = re.sub(r"\s+", " ", NUM.sub(" ", line)).strip(" -:.")
                if len(et) < 3:
                    continue
                kalem.append((sinif(et), cari, et))
            if not kalem:
                continue
            toplam = sum(v for _, v, _ in kalem)
            fark = abs(abs(toplam) - hedef_abs)
            tol = max(2.0, hedef_abs * 0.01)
            rec = {
                "durum": "kapandi" if fark <= tol else "kapanmadi",
                "kur": sum(v for s, v, _ in kalem if s == "kur"),
                "faiz": sum(v for s, v, _ in kalem if s == "faiz"),
                "diger": sum(v for s, v, _ in kalem if s == "diger"),
                "toplam": toplam,
                "hedef": hedef,
                "fark": fark,
                "satir": [{"sinif": s, "tutar": v, "ad": e} for s, v, e in kalem],
            }
            if best is None or (rec["durum"] == "kapandi" and best["durum"] != "kapandi") or fark < best["fark"]:
                best = rec
    return best or {"durum": "baslik_yok", "satir": []}
