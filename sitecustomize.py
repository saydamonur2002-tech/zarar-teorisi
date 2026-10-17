"""Ağ çağrıları için anlık görüntü katmanı (urllib.request.urlopen sarmalayıcısı).

ZT_AG=kaydet     : canlı çek, yanıtı veri_anlik/<sha>.bin'e yaz (anlık görüntü üretimi)
ZT_AG=cevrimdisi : yalnız anlık görüntüden oku; yoksa hata (varsayılan, PYTHONPATH bu dizini içerdiğinde)
ZT_AG=canli      : sarmalayıcı devre dışı
Anahtar = sha256(URL + gövde). Anlık görüntü tarihi: veri_anlik/TARIH.
"""
import hashlib, io, os, urllib.request
from pathlib import Path
_D = Path(__file__).resolve().parent / "veri_anlik"
_MOD = os.environ.get("ZT_AG", "cevrimdisi")
_orj = urllib.request.urlopen

class _Yanit(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def getcode(self): return 200
    status = 200

def _anahtar(req):
    if isinstance(req, str): url, body = req, b""
    else: url, body = req.full_url, (req.data or b"")
    if isinstance(body, str): body = body.encode()
    return hashlib.sha256(url.encode() + b"|" + body).hexdigest()

def urlopen(req, *a, **k):
    if _MOD == "canli": return _orj(req, *a, **k)
    f = _D / (_anahtar(req) + ".bin")
    if _MOD == "cevrimdisi":
        if not f.exists():
            raise RuntimeError(f"çevrimdışı: anlık görüntüde yok ({f.name}); ZT_AG=kaydet ile üret")
        return _Yanit(f.read_bytes())
    with _orj(req, *a, **k) as r: b = r.read()
    _D.mkdir(exist_ok=True); f.write_bytes(b)
    return _Yanit(b)

urllib.request.urlopen = urlopen
