#!/usr/bin/env python3
"""Dosyadaki hukuk anlatımı: HTML kare + kadın Piper sesi + ffmpeg.

Kilitli CSV'lere yazmaz. Taslağı yürürlük kanunu diye okumaz.
Ses: Piper tr_TR-dfki-medium (kadın, CC0). Model repoya girmez.
Çıktı: yayin/anlatim/hukuk_anlatim.mp4 ve .srt
"""
from __future__ import annotations

import shutil
import subprocess
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from piper import PiperVoice
from piper.config import SynthesisConfig

KOK = Path(__file__).resolve().parent
HTML = (KOK / "hukuk.html").as_uri()
CIKTI = KOK / "hukuk_anlatim.mp4"
SRT = KOK / "hukuk_anlatim.srt"
ARA = Path("/tmp/anlatim-hukuk")
MODEL = Path("/tmp/piper-tr/tr_TR-dfki-medium.onnx")
MODEL_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/dfki/tr_TR-dfki-medium.onnx"
MODEL_JSON_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/dfki/tr_TR-dfki-medium.onnx.json"
UZUNLUK = 1.08
ARA_SAHNE = 0.3

SAHNELER = [
    {
        "id": "kapak",
        "baslik": "Anahtar",
        "kare": [("kapak", {})],
        "metin": (
            "Bu video, dosyaların içindeki hukuku anlatır. Defteri değil. "
            "Defter, masada kimin nerede durduğunu sayar. Hukuk, o satırın silinmesine kimin izin verdiğini söyler. "
            "İkisi aynı nesne değildir. "
            "Elinizdeki metin yürürlükteki kanun değildir. Mahkeme kararı da değildir. Çekmecedeki kâğıtların analojisidir. "
            "Bir avlu düşünün. Ortada bir masa. Beş kapı. Masa yükü gösterir. "
            "Kapının üzerindeki anahtar, yükün yer değiştirmesine izin verir. Anahtar yoksa çizgi kâğıtta kalır. "
            "Anahtarı olmayan kapıdan kimse geçemez. Geçen de yükü yok etmez. Yükü yan odaya taşır. "
            "Bu ayrım, bütün videonun omurgasıdır."
        ),
    },
    {
        "id": "defter",
        "baslik": "Masa",
        "kare": [("defter", {})],
        "metin": (
            "Ali, Veli'ye borçlu. Veli'nin kâğıdında aynı sayı alacak diye durur. "
            "Masayı silmek, Ali'yi kurtarmak değildir. Karşılıklı olan kısım iner. Net borç masada kalır. "
            "Bunu bir önceki anlatı saymıştı. Bu videonun sorusu başkadır. O çizgiyi kim çizebilir. "
            "Bir komşu mu. Duvarda asılı bir kural mı. Yoksa henüz mühürlenmemiş bir taslak mı. "
            "Dosya bu üç anahtarı ayrı ayrı koyar. Birini sistem metninin içine yazmamış. "
            "Birini doğrulamış. Birini çekmeceye bırakmış. "
            "Komşu anahtarı iki imzadır. Duvar anahtarı, herkese yazılmış bir kuraldır. "
            "Çekmece anahtarı, henüz kapıya takılmamış bir çizimdir. Üçü de anahtar biçimindedir. Üçü de aynı kapıyı açmaz."
        ),
    },
    {
        "id": "anahtar",
        "baslik": "Birinci kapı",
        "kare": [("anahtar", {})],
        "metin": (
            "Birinci kapı, birbirine kilitlenen faturalardır. "
            "Ali Veli'ye, Veli Ayşe'ye, Ayşe Ali'ye borçluysa üçü aynı halkadadır. "
            "Defter halkayı çizer. Türk dosyalarında bu çizginin adı, sistem metninde bir kanun maddesi olarak yoktur. "
            "Yazılı olan alet şudur. Alacak el değiştirir. Veli, Ali'den olan hakkını Ayşe'ye devreder. "
            "İki taraf birden imza atar. Ortada hakem kasası yoktur. Komşu, komşuya kâğıt verir. "
            "Çok kişinin borcu, ikili devirlerin zinciriyle iner. Buna temlik denir. Alacağın devri. "
            "Borçlar Kanunu'nun tanıdığı komşu işi. Dosya bunu bir üyelik kaydında adlandırır. "
            "Sistemin kendi metni bu katmanı boş bırakır. "
            "Bunu bir sofrada düşünün. Üç kişi birbirine hesap tutmuş. Biri, elindeki hakkı yanındakine uzatır. "
            "İkisi birden adını yazar. Üçüncü kişi masada oturmaz. Hakem de yoktur. Halka, elden ele giden kâğıtla incelir."
        ),
    },
    {
        "id": "dukkan",
        "baslik": "Üyelik dükkânı",
        "kare": [("dukkan", {})],
        "metin": (
            "Bu aleti adlandıran tek Türk kayıt, bir üyelik dükkânıdır. Kapısı gönüllüdür. "
            "Duvara asılmış bir yasa değildir. İçeri giren faturasını koyar. "
            "Uyan iki kâğıt bulunursa devir sözleşmesi çıkar. İki imza birden gerekir. "
            "Dükkânın hacmi, üye sayısı ve tutarı yazılmamıştır. "
            "Bu yüzden dükkân mahsubu çalıştırdı denmez. "
            "Faaliyet dışı bir kayıt da vardır. Site ise canlıdır. Dükkân battı, mahsup çalışmaz da denmez. "
            "Dükkânın kendi cümlesi, yeni komşu geldikçe eşleşme şansının artacağıdır. "
            "Bu, seyrek bir avlunun itirafıdır. Az komşu varsa halka kapanmaz. Ağ, kuraldan önce gelir. "
            "Dükkânın tabelası, devletin mührü değildir. İçeri girmek isteğe bağlıdır. "
            "Çıkan sözleşme, iki komşunun kendi adını yazdığı bir kâğıttır. Kalabalık yoksa, uyacak fatura da az bulunur. "
            "Bu, kuralın zayıflığı değil, avlunun tenhalığıdır."
        ),
    },
    {
        "id": "avlu",
        "baslik": "Başka avlular",
        "kare": [("avlu", {})],
        "metin": (
            "Başka avlularda kural duvara asılmıştır. "
            "Slovenya'da gecikmiş ve tartışmasız borç ayda bir bildirilir. Bildirmeyen, vergi idaresine şikâyet edilir. "
            "Romanya'da kamu şirketinin borcu kurala bağlıdır. Özel şirket gönüllüdür. "
            "Sırp Cumhuriyeti'nde yasa yaptırım yazar. Yaptırım hiç uygulanmamıştır. "
            "Üçünde de nesne aynıdır. Vadesi geçmiş, kavgasız fatura. Bütün masa değil. "
            "Bazı avlularda duvar boştur. İspanya'da ve Portekiz'de komşular kendi anlaşmasıyla oturur. "
            "Portekiz'de bir yasa vardır. Hacim bulunamamıştır. "
            "Ortak resim şudur. Duvara asılan kural da, komşu anlaşması da, yalnız gecikmiş ve kavgasız kâğıdı alır. "
            "Masadaki bütün borcu silmez. Silinen pay küçük kalır. Bildirilenin bir dilimi. Dosya bunu ölçüm diye yazar. "
            "Duvarı olan avluda bile süpürge bütün masayı almaz. Yalnız vadesi gelmiş ve kimsenin itiraz etmediği faturayı alır. "
            "Tartışmalı kâğıt dışarıda kalır. Henüz günü gelmemiş kâğıt da dışarıda kalır. "
            "Bu yüzden silinen dilim, masanın kendisi değildir."
        ),
    },
    {
        "id": "ters",
        "baslik": "Ters kova",
        "kare": [("ters", {})],
        "metin": (
            "O avluların hiçbiri faizi durdurmaz. Kalan borç eski yolundan ödenir. Ödeme planı da yoktur. "
            "Bazı eski kampanyalar kalanı yeni krediyle kapatmıştır. "
            "Kasaya taze su konmuş, halka onunla çözülmüştür. "
            "Dosya bunu üçüncü kapının tersi diye işaretler. "
            "Üçüncü kapı, sisteme giren stokta faizin durmasını ister. "
            "Dünyada bulunan, faizin durması değil, kalanın krediye çevrilmesidir. "
            "En yakın kayıt, bir ülkede bileşik faizin durmasıdır. Faizin kendisinin durduğu bir ulusal kural bulunamamıştır. "
            "Yani üçüncü kapının hukuku, dosyada boş bir askıdır. "
            "Kovayı doldurmak, musluğu kapatmak değildir. Eski kampanyalar kovaya su koymuştur. "
            "Modelin üçüncü kapısı musluğu kısar. Dosya, musluğu kapatan bir ülke kuralı bulamamıştır. "
            "Bulduğu, kovayı dolduran kampanyalardır. Boş askı, bu farkın adıdır."
        ),
    },
    {
        "id": "kira",
        "baslik": "Kira ipi",
        "kare": [("kira", {})],
        "metin": (
            "Doğrulanan tek ip kiradadır. "
            "Ev sahibi kirayı, son on iki ayın fiyat sepetinden hızlı artıramaz. Borçlar Kanunu. "
            "İp geçmişe bağlıdır. Geçen yıl sepet ne kadar şiştiyse, kira en çok o kadar yürür. "
            "İpi ileriye, bir hedefe bağlamak bu bağı keser. Dosya bunu doğrulanmış diye yazar. "
            "Hatırlanan bir tavan daha vardır. İki bin yirmi iki ile yirmi üç arasında kiraya yüzde yirmi beş sınırı. "
            "Bu, hafızadan yazılmıştır. Doğrulanmamıştır. Doğrulanan ip ile hatırlanan tavan aynı nesne değildir. "
            "Beşinci adımın politika kirası ise ayrı bir koldur. Piyasanın altında bir kira, kiracıya nefes, ev sahibine kayıp olur. "
            "Hane toplamı değişmez. O kolun kendi satırı ölçülmedi diye durur. Yasal ip, o kolun yerine geçmez. "
            "İpi bir gemi halatı gibi düşünün. Bir ucu evdedir. Öbür ucu geçen yılın sepetine düğümlüdür. "
            "Sepet ne kadar yükseldiyse halat o kadar uzar. Daha uzağa çekmek, düğümü koparır. "
            "Hatırlanan yüzde yirmi beş, başka bir halattır. Düğümlendiği yer doğrulanmamıştır."
        ),
    },
    {
        "id": "taslak",
        "baslik": "Boş oda taslağı",
        "kare": [("taslak", {})],
        "metin": (
            "Boş oda için çekmecede bir taslak durur. Üzerinde yürürlükte değildir yazar. "
            "Modelin karar kuralının iskeletidir. Oranlar gözlem değil, eşiktir. "
            "Oturduğun oda muaftır. Oturma belgen yoksa muafiyet düşer. "
            "Boş oda için, yılda, beyan edilen değerin yüzde biri kadar bir bedel düşünülür. Lüks boş oda için yüzde beş. "
            "Teklifi reddedebilirsin. Red, bedeli durdurmaz. "
            "Bu el koyma değildir. Kamulaştırma değildir. Sahip evinde kalabilir. "
            "Bedel, boş tutmanın maliyetini boş tutana yüklemek ister. "
            "Işık yanmıyorsa ve kimse oturmuyorsa oda boş sayılır. Muafiyet dilekçe değil, belgedir. "
            "Tadilat, hastalık, miras, satışa çıkmış oda, sınırlı süreyle dışarıda kalır. "
            "Başka bir ülkede işaretlenen evlerin küçük bir kısmı gerçekten bedel ödemiştir. "
            "Taslak bunu bilir. İstanbul için daha yüksek bir tahsilat varsayar. Varsayım, yasa değildir. "
            "Çekmecedeki kâğıdın köşesinde mühür yoktur. Oturulan oda dışarıdadır. Boş oda içeri alınır. "
            "Sahip, teklif edilen kirayı geri çevirebilir. Geri çevirmek, boş tutmanın bedelini silmez. "
            "Ev elinden alınmaz. Bedel, boş duran odanın masrafını o odanın sahibine yazmak ister."
        ),
    },
    {
        "id": "luks",
        "baslik": "Ayrı madde",
        "kare": [("luks", {})],
        "metin": (
            "Lüks bedel ayrı bir maddedir. Mahkeme yalnız onu kaldırırsa, genel bedel ve yerleştirme kâğıtta kalır. "
            "Oturmuş olan çıkarılmaz. Taslak bunu bilerek ayırmıştır. "
            "Model ise paranın büyük kısmının lüks bedelden geldiğini söyler. O madde düşünce kese incelir. "
            "Yalnız lüksün kalkması, bütün bedelin kalkmasına yakın bir yara bırakır. "
            "Bu bir hata diye yazılmamıştır. Ayrı madde, şoku tek odaya hapsetmek içindir. "
            "Para o odadaysa, oda düşünce evin lambası da söner. Taslak bu gerilimi saklamaz. "
            "İki oda düşünün. Birinin kapısı genel bedeldir. Ötekinin kapısı lüks bedeldir. "
            "Mahkeme ikinci kapıyı sökerse birinci kapı duvarda kalır. Ama evin parası ikinci odanın cebindedir. "
            "Kapı sökülünce lamba da kararır. Taslak bu resmi gizlemez."
        ),
    },
    {
        "id": "kapi",
        "baslik": "Ölçü kapısı",
        "kare": [("kapi", {})],
        "metin": (
            "Taslak bütün şehri bir günde açmaz. Önce bir mahalle. Ölç. Kapı tutarsa avlu genişler. "
            "Tutmazsa yeni yerleştirme durur. Oturmuş olan çıkarılmaz. "
            "Kapının dört mandalı vardır. Katılım. Bedelin tahsili. Oturanın ödemesi. Gelirin, verilen desteği taşıması. "
            "Dördü birden tutmalıdır. Biri boşsa kapı açılmaz. "
            "Bu, başarısızlığın gizlenmesi değildir. Ölçülmemiş bir tahsilatın bütün şehre yayılmamasıdır. "
            "Model, sistemin parasının lüks tahsilata dayandığını ve bu tahsilatın hiçbir yerde ölçülmediğini açıkça yazar. "
            "Pilot, o ölçümün kendisi olmak için konmuştur. "
            "Dört mandal bir kapıdır. Biri gevşekse kapı aralanmaz. Önce bir mahallede denenir. "
            "Ölçü tutarsa avlu büyür. Tutmazsa yeni kimse içeri alınmaz. İçeride oturan yerinde kalır. "
            "Bu, şehri bir gecede değiştiren bir ferman değildir."
        ),
    },
    {
        "id": "kagit",
        "baslik": "Ayrı çekmece",
        "kare": [("kagit", {})],
        "metin": (
            "Kâğıt, bu taslağa girmez. Taslağın ilk satırı bunu söyler. Finansal sistem ve senet bu metne girmez. "
            "Ayrı bir dosya vardır. O da yürürlük metni değildir. Tasarım notudur. "
            "Anapara fiyat sepetiyle yürür. Reel getiri sıfırdır. Hedef tutarsa küçük bir ödül vardır. Tutmazsa yoktur. "
            "Gönüllü katılımda bu kâğıt, mevduatın cazibesiyle yarışamaz. "
            "Katılım, kâğıdın tatlılığından değil, boş tutma bedelinin baskısından gelir. Dosya bunu yazar. "
            "Kilitli adım satırı ise hâlâ modellenmedi der. Tasarım notu, o kilidi açmaz. "
            "İki çekmece yan yanadır. Birinde boş odanın taslağı. Ötekinde kâğıdın çizimi. "
            "İkincisi birincinin içine konmamıştır. Çizim de yürürlük metni değildir. "
            "Mevduatın cazibesi dururken bu kâğıt gönüllü olarak tercih edilmez. "
            "İnsanı odaya çağıran, kâğıdın tadı değil, boş tutmanın bedelidir."
        ),
    },
    {
        "id": "sinav",
        "baslik": "Boş sınav",
        "kare": [("sinav", {})],
        "metin": (
            "İki sınav kâğıdı boştur. Mülkiyet maddesi. Vergi maddesi. "
            "Anayasanın otuz beş ve yetmiş üç. Taslak, bu sınavın ayrı olduğunu yazar. Model o kâğıdı doldurmamıştır. "
            "Bedel vergi midir, harç mıdır, adı konmamıştır. "
            "Yüzde beşlik lüks bedel, orantı itirazına açıktır. Etkin tahsilat, modelin en zayıf girdisidir. "
            "Başka bir ülkede işaretlenenin küçük bir payı bedele kalmıştır. İstanbul varsayımı bunun birkaç katıdır. "
            "Varsayım, hüküm değildir. Pilot verisi gelmeden taslak hipotezdir. Dosya bu cümleyi kendi eliyle yazmıştır. "
            "Sınav kâğıdında iki soru boş bırakılmıştır. Mülkiyet. Vergi. Bedelin adı konmamıştır. "
            "Yüzde beş, orantılı mıdır, diye sorulabilir. Dosya bu soruyu cevaplamaz. Cevabı pilota bırakır."
        ),
    },
    {
        "id": "son",
        "baslik": "Söylenecek cümle",
        "kare": [("son", {})],
        "metin": (
            "Söylenecek cümle kısadır. Defter, yükün kimde durduğunu gösterir. "
            "Hukuk, o yükün silinmesine kimin izin verdiğini gösterir. "
            "Birinci kapının anahtarı sistem metninde yoktur. "
            "Bir üyelik dükkânının dosyasında, alacağın devri ve iki imza diye durur. "
            "Başka avlularda duvara asılmış kurallar vardır. Onlar da bütün masayı silmez. Faizi durdurmaz. "
            "Kiradaki ip doğrulanmıştır. Geçmiş on iki ayın sepetine bağlıdır. "
            "Boş oda metni taslaktır. Yürürlükte değildir. Teklif reddedilebilir. El koyma değildir. "
            "Mülkiyet ve vergi sınavı verilmemiştir. Üç kilit boşken bu paket bir kanun önerisi değildir. "
            "Anahtar, çekmecede duran bir iskelettir. "
            "Masa durur. Kapı, anahtar takılınca konuşur. Anahtar takılmadan çizilen ok, bir yön gösterir. Hüküm olmaz."
        ),
    },
]


def _url(sahne: str) -> str:
    return HTML + "?kare=" + sahne


def sure(yol: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(yol)],
        text=True,
    )
    return float(out.strip())


def cek(url: str, hedef: Path) -> None:
    hedef.parent.mkdir(parents=True, exist_ok=True)
    ud = hedef.parent / ("ud-" + hedef.stem)
    if ud.exists():
        shutil.rmtree(ud, ignore_errors=True)
    proc = subprocess.Popen(
        [
            "google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--force-device-scale-factor=1",
            "--window-size=1280,720", f"--user-data-dir={ud}",
            "--virtual-time-budget=4000", f"--screenshot={hedef}", url,
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    son = -1
    for _ in range(50):
        time.sleep(0.2)
        if hedef.exists():
            n = hedef.stat().st_size
            if n > 8000 and n == son:
                break
            son = n
    proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
    shutil.rmtree(ud, ignore_errors=True)
    if not hedef.exists() or hedef.stat().st_size < 8000:
        raise RuntimeError(f"kare boş: {hedef}")


def modeli_hazirla() -> PiperVoice:
    if not MODEL.exists() or MODEL.stat().st_size < 1_000_000:
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["curl", "-fL", "--retry", "3", "-o", str(MODEL), MODEL_URL])
        subprocess.check_call(["curl", "-fL", "--retry", "3", "-o", str(MODEL) + ".json", MODEL_JSON_URL])
    return PiperVoice.load(str(MODEL))


def seslendir(ses: PiperVoice, metin: str, hedef: Path) -> None:
    with wave.open(str(hedef), "wb") as wav:
        ses.synthesize_wav(metin, wav, syn_config=SynthesisConfig(length_scale=UZUNLUK))


def sahne_video(png: Path, ses: Path, cikti: Path, dur: float) -> None:
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(png), "-i", str(ses),
            "-vf", "scale=1280:720,setsar=1,fps=8,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "28",
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(cikti),
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def srt_yaz(satirlar: list[tuple[float, float, str]], yol: Path) -> None:
    def damga(saniye: float) -> str:
        saniye = max(0.0, saniye)
        saat, kalan = divmod(int(saniye), 3600)
        dakika, sn = divmod(kalan, 60)
        ms = int(round((saniye - int(saniye)) * 1000))
        return f"{saat:02d}:{dakika:02d}:{sn:02d},{ms:03d}"

    yol.write_text(
        "\n".join(f"{i}\n{damga(a)} --> {damga(b)}\n{metin}\n" for i, (a, b, metin) in enumerate(satirlar, 1)),
        encoding="utf-8",
    )


def main() -> None:
    if ARA.exists():
        shutil.rmtree(ARA)
    ARA.mkdir(parents=True)
    print("ses")
    ses = modeli_hazirla()
    (ARA / "ses").mkdir()
    sureler = {}
    for s in SAHNELER:
        yol = ARA / "ses" / f"{s['id']}.wav"
        seslendir(ses, s["metin"], yol)
        sureler[s["id"]] = sure(yol)
        print("ses", s["id"], f"{sureler[s['id']]:.1f}s")
    toplam = sum(sureler.values()) + ARA_SAHNE * (len(SAHNELER) - 1)
    print(f"konusma {toplam / 60:.2f} dk")
    if not (600 <= toplam <= 900):
        raise SystemExit(f"süre bandın dışında: {toplam:.0f} sn")
    print("kare")
    (ARA / "kare").mkdir()

    def bir(s):
        yol = ARA / "kare" / f"{s['id']}.png"
        cek(_url(s["id"]), yol)
        return s["id"], yol

    kare = {}
    for i in range(0, len(SAHNELER), 4):
        with ThreadPoolExecutor(max_workers=4) as havuz:
            for ad, yol in havuz.map(bir, SAHNELER[i:i + 4]):
                kare[ad] = yol
                print("kare", yol.name, yol.stat().st_size)
    parcalar = []
    srt = []
    imlec = 0.0
    (ARA / "parca").mkdir()
    for s in SAHNELER:
        oturum = sureler[s["id"]] + ARA_SAHNE
        parca = ARA / "parca" / f"{s['id']}.mp4"
        sahne_video(kare[s["id"]], ARA / "ses" / f"{s['id']}.wav", parca, oturum)
        parcalar.append(parca)
        srt.append((imlec, imlec + sureler[s["id"]], s["baslik"] + ". " + s["metin"]))
        imlec += oturum
        print("parca", s["id"], f"{sure(parca):.1f}s")
    liste = ARA / "liste.txt"
    liste.write_text("".join(f"file '{p}'\n" for p in parcalar), encoding="utf-8")
    subprocess.check_call(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy", str(CIKTI)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    srt_yaz(srt, SRT)
    print(f"video {CIKTI} {CIKTI.stat().st_size / 1e6:.1f} MB {sure(CIKTI) / 60:.2f} dk")


if __name__ == "__main__":
    main()
