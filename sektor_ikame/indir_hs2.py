"""HS2 fasıl ticareti. Katsayı yok. Kayıt her istekten sonra yazılır."""
import json
import ssl
import time
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent
ctx = ssl.create_default_context()
kapsam = json.loads((KOK / "kapsam.json").read_text())
reps = [int(k) for k, v in kapsam["reporters"]["2018"].items() if v]
out_path = KOK / "hs2.json"
out = json.loads(out_path.read_text()) if out_path.exists() else {"tur_x": {}, "tur_m": {}, "dunya": {}}


def pull(rep, year, flow):
    u = (
        "https://comtradeapi.un.org/public/v1/preview/C/A/HS?"
        f"reporterCode={rep}&period={year}&flowCode={flow}&cmdCode=AG2"
        "&partnerCode=0&partner2Code=0&customsCode=C00&motCode=0&maxRecords=500"
    )
    req = urllib.request.Request(u, headers={"User-Agent": "research", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
        d = json.loads(r.read().decode())
    rows = {}
    for row in d.get("data") or []:
        code = str(row.get("cmdCode"))
        if code.isdigit() and len(code) <= 2:
            rows[code] = {"v": row.get("primaryValue") or 0.0, "kg": row.get("netWgt") or 0.0}
    return rows


def have(bucket, rep, year):
    if bucket == "dunya":
        return str(rep) in out["dunya"].get(str(year), {})
    key = "tur_x" if bucket == "tur_x" else "tur_m"
    return str(year) in out[key]


def store(bucket, rep, year, rows):
    if bucket == "dunya":
        out["dunya"].setdefault(str(year), {})[str(rep)] = rows
    else:
        out[bucket][str(year)] = rows
    out_path.write_text(json.dumps(out))


jobs = []
for y in range(2013, 2025):
    jobs.append(("tur_x", 792, y))
    jobs.append(("tur_m", 792, y))
for y in (2017, 2018, 2019):
    for rep in reps:
        jobs.append(("dunya", rep, y))

done = 0
for bucket, rep, year in jobs:
    flow = "M" if bucket == "tur_m" else "X"
    if have(bucket, rep, year):
        done += 1
        continue
    ok = False
    for attempt in range(3):
        try:
            rows = pull(rep, year, flow)
            store(bucket, rep, year, rows)
            print(bucket, rep, year, len(rows), flush=True)
            ok = True
            break
        except Exception as e:
            print("retry", bucket, rep, year, type(e).__name__, flush=True)
            time.sleep(3 + attempt * 2)
    if not ok:
        print("FAIL", bucket, rep, year, flush=True)
    time.sleep(0.6)
print("bitti", done, "ustune", flush=True)
