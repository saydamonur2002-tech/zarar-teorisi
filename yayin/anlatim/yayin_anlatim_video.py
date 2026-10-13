#!/usr/bin/env python3
"""Tek Sistem anlatım videosu: HTML kare + Piper sesi + ffmpeg.

Kilitli CSV'lere yazmaz. Üç kapı boşken reçete cümlesi kurmaz.
Çalıştırma: python3 yayin/anlatim/yayin_anlatim_video.py
Çıktı: yayin/anlatim/tek_sistem_anlatim.mp4 ve .srt
Ara dosyalar /tmp/anlatim altında kalır.

Ses: Piper tr_TR-fahrettin-medium (CC0). Edge uç noktası 403 verdiği için
yerel model kullanılır. Model repoya girmez; yoksa aynadan iner.
"""
from __future__ import annotations

import shutil
import subprocess
import time
import wave
from pathlib import Path

from piper import PiperVoice
from piper.config import SynthesisConfig

KOK = Path(__file__).resolve().parent
HTML = (KOK / "index.html").as_uri()
CIKTI = KOK / "tek_sistem_anlatim.mp4"
SRT = KOK / "tek_sistem_anlatim.srt"
ARA = Path("/tmp/anlatim")
MODEL = Path("/tmp/piper-tr/tr_TR-fahrettin-medium.onnx")
MODEL_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/fahrettin/tr_TR-fahrettin-medium.onnx"
MODEL_JSON_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/fahrettin/tr_TR-fahrettin-medium.onnx.json"
# 1.0 yaklaşık on iki dakika. Biraz yavaşlatmak netliği artırır.
UZUNLUK = 1.05
ARA_SAHNE = 0.35

# kare: (sahne kimliği, kaydırıcı). Kaydırıcı değerleri sayfadaki aralık birimindedir.
SAHNELER = [
    {
        "id": "kapak",
        "baslik": "Kapak",
        "kare": [("kapak", {})],
        "metin": (
            "Bu video, Zarar Teorisi denilen kapalı defteri sadeleştirir. "
            "Beş aktör var: hane, firma, banka, kamu ve dışarı. "
            "Birinin borcu, başkasının alacağıdır. Toplam uydurulmaz. Yük yer değiştirir. "
            "Ekrandaki sayılar iki bin yirmi altının ilk çeyreğidir. "
            "Hane artı yirmi bir virgül dört trilyon lira. Firma eksi otuz virgül bir. "
            "Banka neredeyse sıfırdadır, çünkü aracıdır. Parayı tutar, krediyi açar, zararı biriktirmez. "
            "Kamu eksi altı virgül dört. Dışarı artı on beş virgül altı. Artı, alacaklı taraf demektir. "
            "Bu bir politika reçetesi değildir. Ölçülen, üst sınır ve varsayım ayrı durur. "
            "Alttaki siyah şerit, videonun senaryosunu taşır. "
            "Silinen yüzde yirmi. Faize giren pay dörtte bir. Mevduattan kâğıda yüzde yirmi beş. "
            "Kiracı kapsamı yüzde yirmi. Bunlar ölçüm değil. Tavanın içinde duran varsayımdır."
        ),
    },
    {
        "id": "defter",
        "baslik": "Defter",
        "kare": [("defter", {})],
        "metin": (
            "Her çeyrek, her aktör için aynı satır kapanır. "
            "Bugünkü yer, dünkü yer artı bugünkü işlem artı fiyatın yazdığı farktır. "
            "Teknik adı net finansal pozisyon, net işlem ve değerlemedir. "
            "Halk diliyle: masadaki yer, kasadan geçen para ve kurun kâğıda yazdığı düzeltme. "
            "Ali, Veli'ye borçluysa Veli'nin alacağı aynı satırdadır. "
            "Kur sıçrarsa ikisinin kâğıdı birden değer değiştirir. Bu bir ödeme değildir. "
            "Kimse kimseye para vermeden stok değişir. "
            "Çubukta sıfır ortadadır. Mavi alacaklı, kırmızı borçlu. "
            "Firma bu çeyrek işlemden yaklaşık bir virgül dört trilyon eksi yazdı. "
            "Değerlemeden bir trilyona yakın eksi daha geldi. Yük hem aktı hem fiyatlandı. "
            "Çekirdek şudur. Biri ödeyemezse karşı tarafın alacağı da durur. "
            "Kayıp yok olmaz. Bir yerde oturmak zorundadır."
        ),
    },
    {
        "id": "aktor",
        "baslik": "Aktörler",
        "kare": [("aktor", {})],
        "metin": (
            "Beş kişi. Hane, maaş, taksit ve kiradır. Teknikte on dördüncü ve on beşinci sektördür. "
            "Pozisyonu artı yirmi bir virgül dört trilyon. Toplam hane sakin görünür. Alt grup gergindir. "
            "Asgari ücretli hane, modelin kendi vekilidir. "
            "Borç payı yüzde kırk, servis yüzde otuz beş, asgari ücrete bölünür. "
            "Çıkan oran yüzde kırk yedidir. Bu bir parametredir. Her hanenin ölçümü değildir. "
            "Firma malı satar, faizi öder, anaparayı her yıl yeniler. "
            "Finansman gideri, faaliyet giderinin sıfır virgül seksen dördüdür. İki bin yirmi dört ölçümü. "
            "Rejim okuması spekülatiftir. Banka tezgâhtır. Zararı dağıtır, biriktirmez. "
            "Kamu, vergi, harcama ve merkez bankasıdır. Faizin harcamaya oranı yüzde on dört virgül dörttür. "
            "Dışarı, içeride biriken eksiğin aynasıdır. Çeyrekte yaklaşık bir virgül yedi trilyon net işlemle büyür. "
            "Üç rejim vardır. Resmi kriz tarihi değildir. "
            "Hedge: taksiti maaştan bitirirsin. Spekülatif: faizi ödersin, anaparayı yenilersin. "
            "Ponzi: faizi de yeni borçla ödersin. "
            "Eşik senaryodur. Hane için servis bölü gelir, yüzde otuzun altı hedge, "
            "otuz ile kırk spekülatif, kırkın üstü ponzi etiketidir. "
            "Firma için finansman bölü faaliyet, sıfır virgül ellinin altı, elliden bire, birin üstü. "
            "Firma ölçümle ortadadır. Asgari vekil, model bandında ponzi etiketindedir."
        ),
    },
    {
        "id": "sorun",
        "baslik": "Sorun",
        "kare": [("sorun", {})],
        "metin": (
            "Tek delik yok. Aynı yük beş kapıdan girer. Birimler farklıdır. "
            "Milyar stok, yüzde oran ve metrekare kirası tek çubukta toplanmaz. "
            "Bir. Firmaların birbirine borcu, otuz dokuz bin dokuz yüz yirmi dokuz milyar. Ölçüm, brüt. "
            "İki. Firma takip oranı yüzde iki virgül elli iki. Eylül iki bin yirmi altı. "
            "Üç. Firma kredi stoğu yirmi beş bin üç yüz kırk milyar. Ticari faiz yüzde elli üç. "
            "Dört. Üç mevduat adresi, on dokuz bin üç yüz altmış iki milyar. "
            "Yeni kredi, milli gelirin yüzde yedi virgül altmış ikisidir. "
            "Beş. Birim kira, metrekarede ayda iki yüz elli sekiz lira. "
            "Yıllık fiyat artışı yüzde yirmi dokuz virgül yedidir. "
            "Döngü şöyledir. Kilitli borç ödenmeyince yeni kredi istenir. Yeni kredi faiz doğurur. "
            "Faiz mevduatı şişirir. Mevduat yine kredi olur. Kira ve fiyat haneyi sıkar. "
            "Hane alınca firmanın tahsilatı düşer. "
            "Musluklar birbirine bağlıdır. Birini kısınca öteki akıyorsa yük yer değiştirir, bitmez."
        ),
    },
    {
        "id": "harita",
        "baslik": "Beş adım, sıra",
        "kare": [("harita", {})],
        "metin": (
            "Sıra kilitlidir. Önce mahsup. Karşılıklı borç düşer, net borç aynı kalır. Pencere iki bin yirmi yedidir. "
            "İkinci adım onunla birlikte yürür. Kalan sırayla ödenir. Vadesini uzatan kesilir. "
            "Üçüncü adım iki bin yirmi sekiz rampasıdır. Sisteme giren stokta faiz tahakkuku durur. "
            "Dördüncü adım iki bin yirmi dokuzdur. Mevduatın bir payı kâğıda geçer. "
            "Beşinci adım ayrı koldur. Politika kirası piyasanın altında kalır. "
            "Pencereler örtüşmez. Bir adımın sayısı, diğerinin sonuç sütununa yazılmaz. "
            "Önce birbirine borçlu olanların kâğıdı karşılaştırılır. "
            "Gerisi, kalan yükün faizini ve yeni krediyi keser. Kira, hanenin yaşam satırıdır."
        ),
    },
    {
        "id": "adim1",
        "baslik": "Adım 1, mahsup",
        "kare": [("adim1", {})],
        "metin": (
            "Birinci adım önceliklidir. Ali, Veli'ye yüz borçlu. Veli, Ali'ye seksen borçlu. "
            "Seksen düşer. Ali'de yirmi kalır. Net borçlu yine borçludur. Bu iflas değildir. "
            "Ödenmeden duran, ben sana sen bana kısmı gider. Asıl borç masada kalır. "
            "Hazneler arası brüt, yetmiş sekiz bin sekiz yüz yetmiş milyar. "
            "Karşılıklı düşebilen ortak, yirmi bin üç yüz altmış üç milyar. "
            "Tavan sıfır virgül iki bin beş yüz seksen ikidir. Üst sınırdır. Gerçekleşen mahsup değildir. "
            "Eski tavan sıfır virgül sıfır yedi yüz yirmi sekizdi. Aynı aracıyı birden çok satırda saydığı için durur. "
            "Firma içi ticari borç ayrı nesnedir. Otuz dokuz bin dokuz yüz yirmi dokuz milyar. "
            "İki bin yirmi altı, ilk çeyrek ölçümü. "
            "Tabloda altı çift var. En büyüğü firma ile banka, sonra hane ile banka. "
            "Kimden kime bilançosu yoktur. Kilitli dosyada silinen sütunu boştur ve boş kalır."
        ),
    },
    {
        "id": "y20",
        "baslik": "Eşik yüzde 20",
        "kare": [("y20", {"oran": "20"})],
        "metin": (
            "Beşte biri silinebiliyorsa birinci kapı açılır. Bu ölçülmedi. "
            "Üç taban var. Üçü de kendi tavanının içindedir. "
            "Yüzde yirmide, iki bin yirmi dört ticari borçtan iki bin sekiz yüz altmış yedi milyar düşer. "
            "Tavan on üç bin yüz bir. Oran sıfır virgül yirmi iki. "
            "Firma içi diğer borçtan yedi bin dokuz yüz seksen altı milyar. "
            "Tavan otuz altı bin dört yüz doksan bir. Yine sıfır virgül yirmi iki. "
            "Hazneler arası brütten on beş bin yedi yüz yetmiş dört milyar. "
            "Tavan yirmi bin üç yüz altmış dört. Oran sıfır virgül yetmiş yedi. Yakın, delinmemiş. "
            "Çubuk, silinenin tavana oranıdır. Sağ kenar tavandır. "
            "Firma içinde çubuk kısa kalır. Haznede uzundur ama kenara değmez. "
            "Tam çizim yaklaşık yüzde doksan siler. Yüzde yirmi temkinli varsayımdır. "
            "İçinde olmak olabilirliktir. Yüzde yirmi silindi, yazılmaz."
        ),
    },
    {
        "id": "y20b",
        "baslik": "Eşik, kaydırıcı",
        "esit": True,
        "kare": [
            ("y20", {"oran": "10"}),
            ("y20", {"oran": "15"}),
        ],
        "metin": (
            "Şimdi oranı yüzde ondan yukarı çekiyorum. "
            "Silinen sütun ve çubuk onunla yürür. Onda çubuklar kısa kalır."
        ),
    },
    {
        "id": "y20c",
        "baslik": "Eşik, tavan aşımı",
        "kare": [("y20", {"oran": "30"})],
        "metin": (
            "Otuzda hazneler arası oran bir virgül on altıya çıkar. "
            "Tavan aşılmıştır. Çubuk kırmızıya döner."
        ),
    },
    {
        "id": "y20d",
        "baslik": "Eşik, yüzde 20",
        "kare": [("y20", {"oran": "20"})],
        "metin": (
            "Bu yüzden video yüzde yirmide durur. Yirmi, üç tabanda da tavanın içindedir. "
            "Kaydırıcı ölçüm üretmez. Varsayım bandını gösterir."
        ),
    },
    {
        "id": "adim2",
        "baslik": "Adım 2, ödeme sırası",
        "kare": [("adim2", {})],
        "metin": (
            "İkinci adım. Kalan borç sırayla ödenir. Tepedeki taraf vadesini uzatamaz. "
            "Modelde on yedi sektör düğümü var. Nakit ve ücret, iki bin yirmi dört ölçümüdür. "
            "Kenarların kime gittiği varsayımdır. "
            "Tam çizimde on beş sektör brüt temerrüttedir. Mahsup sonrası sıfır. "
            "Köprü kredi ihtiyacı, sekiz bin üç yüz yirmi dokuz milyardan sıfıra iner. Silinen yüzde seksen sekiz. "
            "Yüzde yirmide bu sıfır çıkmaz. Kalan yüzde seksen hâlâ ödenmek zorundadır. "
            "Ücrete gidebilecek payın tavanı sıfır virgül sıfır kırk dörttür. "
            "Sentetik sıfır virgül otuz, bu tavanın yaklaşık yedi katıdır ve tablonun dışındadır. "
            "Firma takip oranı ölçümde yüzde iki virgül elli ikidir. Modeldeki sıfır buna eşitlenmez. "
            "Nakit yüzde on bir kısılınca bir sektör yine düşer. Tarımda ücret ölçülemedi. "
            "Halk diliyle: kilit kalkınca sırada bekleyen öder. Kasayı tutan, yarın öderim diyemez. "
            "İşçinin payı ise sanılandan küçüktür."
        ),
    },
    {
        "id": "adim3",
        "baslik": "Adım 3, faiz",
        "kare": [("adim3", {})],
        "metin": (
            "Üçüncü adım faizdir. Sisteme giren kredide faiz işlemeyi bırakır. "
            "Firma kazanır, banka kaybeder, toplam sıfırdır. Para yok olmaz. "
            "Stok, firmanın kredi hesabıdır. Yirmi beş bin üç yüz kırk milyar. "
            "Ticari faiz yüzde elli üç virgül iki. Eylül iki bin yirmi altı. "
            "Sonrasının sabit kaldığı varsayımdır. "
            "Etkin pay sıfır virgül otuz altı. İki bin yirmi dört finansman giderinin, faiz çarpı stoka oranıdır. "
            "Kappa, bu stoğun ne kadarının sisteme girdiğidir. Dörtte bir, yarım, ya da tamamı. "
            "Rampa iki bin yirmi sekiz. Tam yıl iki bin yirmi dokuzdan itibaren. "
            "Dörtte birde yılda yaklaşık bin iki yüz sekiz milyar. Yarıda iki bin dört yüz on beş. "
            "Tamamında dört bin sekiz yüz otuz bir. "
            "Yüzde yirmi eşiğine en yakın bant dörtte birdir. İki bin yirmi dört giderinin yaklaşık beşte ikisi. "
            "Ticari mahsup stoğu ile bu kredi aynı nesne değildir. "
            "Kilitli adım dosyasında kural, modellenmedi diye durur. Sayı yan dosyadadır. "
            "Faiz durdu, firma kurtuldu, denmez."
        ),
    },
    {
        "id": "adim4",
        "baslik": "Adım 4, adres",
        "kare": [("adim4", {})],
        "metin": (
            "Dördüncü adım adrestir. Vadeli mevduatın bir payı kâğıda döner. "
            "Bankanın yeni kredi itişi incelir. Üç adres ölçülmüştür. "
            "Hane vadeli, sekiz bin üç yüz yirmi iki milyar. Firma vadeli, dört bin dört yüz. "
            "Gerçek kişi döviz mevduatı, altı bin altı yüz otuz dokuz. Toplam on dokuz bin üç yüz altmış iki milyar. "
            "Teta, bunun ne kadarının döndüğüdür. Yüzde on, yirmi beş veya elli. "
            "Vade sekiz çeyrektir. Yenileme ya sıfır ya yarı yarıya. Prim yılda yüzde iki veya beş. "
            "Hedef endeksi depoda yoktur. Hesaplanmadı. "
            "Yüzde yirmi beşte tepe stok dört bin sekiz yüz kırk milyar. "
            "Kredi itişi yılda yaklaşık üç yüz seksen yedi milyar azalır. "
            "Katsayı sıfır virgül sıfır sekiz, kademe sabitidir. Ölçüm değildir. "
            "Prim, iki bin otuz birde yirmi dört ile üç yüz doksan üç milyar arasında kalır. "
            "Duran faizin yanında küçüktür. "
            "Kâğıt satırı kilitli dosyada modellenmedi. Bu bir banttır. "
            "İnsan parasını bankadan çekip başka bir kâğıda koyar. Kimse batmaz. Yer değişir. "
            "Pencere iki bin yirmi dokuzdur. Yüzde yirmi eşiği bu adımı açmaz."
        ),
    },
    {
        "id": "adim5",
        "baslik": "Adım 5, kira",
        "kare": [("adim5", {})],
        "metin": (
            "Beşinci adım kiradır. Politika kirası piyasanın altında kalırsa kiracı kazanır, ev sahibi kaybeder. "
            "Hane toplamı değişmez. Birim kira ölçümüdür. Metrekarede ayda iki yüz elli sekiz lira. "
            "İkinci çeyrek. Değerlemesi yapılan konut. "
            "Doksan ile yüz on metrekarede, kiracı başına ayda yirmi üç bin ile yirmi sekiz bin lira. "
            "Havuz kirası ayda yirmi bin liradır. Bu modeldir. Piyasaya oranı sıfır virgül yetmiş yedi. "
            "Fark, kiracı başına ayda üç bin ile sekiz bin lira. "
            "Hane sayısı yirmi altı virgül dört milyon elle yazılmıştır. Doğrulanmamıştır. "
            "Kiracı oranı yüzde yirmi beş ile otuz, varsayımdır. "
            "Kapsam yüzde yirmiyse, yılda ev sahibinden kiracıya elli iki ile yüz altmış milyar geçer. "
            "Yarı kapsamda yüz yirmi dokuz ile dört yüz bir. Tam kapsamda iki yüz elli sekiz ile sekiz yüz bir. "
            "Yıllık kira akışının kendisi bin sekiz yüz ile iki bin yedi yüz milyar arasındadır. "
            "Depodaki konut payı ayrı bir nesnedir. Buna eklenmez. "
            "Kilitli kira satırı ölçülmedi kalır. "
            "Buradaki yüzde yirmi, kiracıların beşte biridir. Birinci adımdaki silinen oranından başka şeydir. "
            "Kurumsal ev sahibi bu satırda görünmez."
        ),
    },
    {
        "id": "esik",
        "baslik": "Eşik ve senaryo",
        "kare": [
            ("esik", {}),
            ("esik", {"oran": "10", "k": "25", "t": "10", "c": "20"}),
            ("esik", {"oran": "30", "k": "50", "t": "50", "c": "50"}),
            ("esik", {"oran": "20", "k": "100", "t": "25", "c": "100"}),
            ("esik", {}),
        ],
        "metin": (
            "Ölçülen çekirdek durur. Band, senaryodur. "
            "Servis bölü gelir bantları yüzde otuz ve kırk. Firma bantları sıfır virgül elli ve bir. "
            "Bunlar rejim okumasıdır. Resmi kriz ilanı değildir. "
            "Silinen oran yüzde yirmi. Birinci kapının varsayımı. "
            "Kappa sıfır virgül yirmi beş. Faizi duran stok payı. "
            "Teta sıfır virgül yirmi beş. Mevduattan kâğıda pay. Kiracı kapsamı yüzde yirmi. "
            "Ücret tavanı sıfır virgül sıfır kırk dört. Üst sınırdır. "
            "Kredi itiş payı sıfır virgül sıfır sekiz. Kademe sabitidir. "
            "Geçiş payı boştur. Kapı kilitlidir. "
            "Kaydırıcıyı oynatmak ölçüm üretmez. Bu varsayım tutarsa sayı bu bandın içindedir, der. "
            "Üç kilit boşken paket öneri olmaz. Silinen sütun, kâğıt satırı ve geçiş. "
            "Şimdi şeridi gezdiriyorum. Oran, kappa, teta ve kapsam değişince alttaki sayılar yürür. "
            "Etiket yine varsayım kalır."
        ),
    },
    {
        "id": "enf",
        "baslik": "Enflasyon",
        "kare": [("enf", {})],
        "metin": (
            "Kredi itişi kesilirse fiyat aşağı baskılanır. Ne kadar, kapı boştur. "
            "İki bin yirmi beş itişi, milli gelirin yedi virgül altmış iki puanıdır. "
            "Etki, geçiş payı çarpı kesilen itiş, eksi işaretlidir. "
            "Geçiş sıfır ile bir arasındadır. Nokta tahmin sıfır virgül doksan dört. "
            "Standart hata sıfır virgül yetmiş dört. Kırk iki çeyrek. "
            "İki bin on beşten, iki bin yirmi beşin sonuna. "
            "Yüzde doksan beş aralığı çubuğun tamamını kapsar. Tek sayı yazılmaz. "
            "Altmış sekizlik okuma, geçişi kabaca sıfır virgül yirmi ile bir arasına çeker. "
            "İtişin tamamı kesilirse beş yıllık fiyat, en az bir virgül beş, en çok yedi virgül altı puan aşağı baskılanır. "
            "Yön aşağı ağırlıklıdır. Kesinlik yoktur. Yedi virgül altı puan iner, denmez. "
            "Anket, iki bin yirmi yedide yüzde yirmi iki virgül yedi. "
            "İki bin yirmi sekizde yüzde on sekiz virgül üç. İki bin otuz birde yüzde on iki virgül bir. "
            "Bant, anketin altına bu aralığı indirir. Anketin yerine geçmez. "
            "Faiz durması ve kira da fiyatı aşağı iter. Onların geçişi ölçülmedi. Bu banda yazılmadı. "
            "Ücret kanalı zayıf ve yukarı doğrudur."
        ),
    },
    {
        "id": "son",
        "baslik": "Sözün sınırı",
        "kare": [("son", {})],
        "metin": (
            "Yön doğrudur. Miktar, kapı dolmadan yazılmaz. "
            "Beş adım kuruldu, denmez. Şu adım şu etikettedir. Üç kapı boştur. "
            "Stok yüzde yirmi silindi, denmez. Varsayımdır. Üç taban tavanın içindedir. Sütun boştur. "
            "Firmalar kurtuldu, denmez. Net borç aynıdır. Kilitli brüt gider. "
            "Faiz durdu, herkes rahatladı, denmez. Kappa varsayımdır. Toplam sıfırdır. Yer değişir. "
            "Kâğıt hazır, denmez. Satır modellenmedi. Bant ayrı dosyadadır. "
            "Enflasyon yedi virgül altı puan iner, denmez. Banttır. Kapı boştur. "
            "Kırılma şu tarihtedir, denmez. Gerilim izlenir. Hat kesilmesi ölçülmedi. "
            "Defter, yükün kimde durduğunu gösterir. Beş kesik o yükü sırayla inceltir. "
            "Ölçülmeyen yer, varsayım diye işaretlidir. Öneri, kapı dolunca kurulur."
        ),
    },
]


def _url(sahne: str, kaydirici: dict) -> str:
    qs = ["kare=" + sahne]
    for anahtar, deger in kaydirici.items():
        qs.append(f"{anahtar}={deger}")
    return HTML + "?" + "&".join(qs)


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
    ayar = SynthesisConfig(length_scale=UZUNLUK)
    with wave.open(str(hedef), "wb") as wav:
        ses.synthesize_wav(metin, wav, syn_config=ayar)


def zamanla(kareler: list, toplam: float, esit: bool) -> list[tuple[Path, float]]:
    if len(kareler) == 1:
        return [(kareler[0], toplam)]
    if esit:
        parca = toplam / len(kareler)
        return [(k, parca) for k in kareler]
    ilk = toplam * 0.62
    kalan = (toplam - ilk) / (len(kareler) - 1)
    return [(kareler[0], ilk)] + [(k, kalan) for k in kareler[1:]]


def sahne_video(kareler: list[tuple[Path, float]], ses: Path, cikti: Path) -> None:
    args = ["ffmpeg", "-y"]
    for png, dur in kareler:
        args += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(png)]
    args += ["-i", str(ses)]
    parca = []
    for i in range(len(kareler)):
        parca.append(f"[{i}:v]scale=1280:720,setsar=1,fps=8,format=yuv420p[v{i}]")
    birles = "".join(f"[v{i}]" for i in range(len(kareler)))
    birles += f"concat=n={len(kareler)}:v=1:a=0[v]"
    args += [
        "-filter_complex", ";".join(parca) + ";" + birles,
        "-map", "[v]", "-map", f"{len(kareler)}:a",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "28",
        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
        str(cikti),
    ]
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def srt_yaz(satirlar: list[tuple[float, float, str]], yol: Path) -> None:
    def damga(saniye: float) -> str:
        saniye = max(0.0, saniye)
        saat, kalan = divmod(int(saniye), 3600)
        dakika, sn = divmod(kalan, 60)
        ms = int(round((saniye - int(saniye)) * 1000))
        return f"{saat:02d}:{dakika:02d}:{sn:02d},{ms:03d}"

    govde = []
    for i, (a, b, metin) in enumerate(satirlar, 1):
        govde.append(f"{i}\n{damga(a)} --> {damga(b)}\n{metin}\n")
    yol.write_text("\n".join(govde), encoding="utf-8")


def sesleri_al() -> dict[str, Path]:
    (ARA / "ses").mkdir(parents=True, exist_ok=True)
    ses = modeli_hazirla()
    hedefler = {}
    for s in SAHNELER:
        yol = ARA / "ses" / f"{s['id']}.wav"
        seslendir(ses, s["metin"], yol)
        hedefler[s["id"]] = yol
        print("ses", s["id"], f"{sure(yol):.1f}s")
    return hedefler


def kareleri_cek() -> dict[tuple, Path]:
    istenen = []
    gorulen = set()
    for s in SAHNELER:
        for sahne, kaydirici in s["kare"]:
            anahtar = (sahne, tuple(sorted(kaydirici.items())))
            if anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            ek = "-".join(f"{a}{b}" for a, b in kaydirici.items())
            ad = f"{sahne}-{ek}" if ek else sahne
            istenen.append((anahtar, ARA / "kare" / f"{ad}.png", _url(sahne, kaydirici)))
    (ARA / "kare").mkdir(parents=True, exist_ok=True)

    def bir(paket):
        anahtar, yol, url = paket
        cek(url, yol)
        return anahtar, yol

    # Dört krom birden. Kalanı sırayla dalgalar.
    bitti = {}
    dalga = 4
    for i in range(0, len(istenen), dalga):
        dilim = istenen[i:i + dalga]
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=dalga) as havuz:
            for anahtar, yol in havuz.map(bir, dilim):
                bitti[anahtar] = yol
                print("kare", yol.name, yol.stat().st_size)
    return bitti


def main() -> None:
    if ARA.exists():
        shutil.rmtree(ARA)
    ARA.mkdir(parents=True)
    print("ses")
    ses_yol = sesleri_al()
    sureler = {k: sure(v) for k, v in ses_yol.items()}
    toplam = sum(sureler.values()) + ARA_SAHNE * (len(SAHNELER) - 1)
    print(f"konusma {toplam/60:.2f} dk")
    for s in SAHNELER:
        print(f"  {s['id']:8} {sureler[s['id']]:6.1f}s")
    if not (600 <= toplam <= 900):
        raise SystemExit(f"süre bandın dışında: {toplam:.0f} sn")
    print("kare")
    kare = kareleri_cek()
    parcalar = []
    srt = []
    imlec = 0.0
    for s in SAHNELER:
        dosyalar = []
        for sahne, kaydirici in s["kare"]:
            anahtar = (sahne, tuple(sorted(kaydirici.items())))
            dosyalar.append(kare[anahtar])
        oturum = sureler[s["id"]] + ARA_SAHNE
        plan = zamanla(dosyalar, oturum, bool(s.get("esit")))
        parca = ARA / "parca" / f"{s['id']}.mp4"
        parca.parent.mkdir(parents=True, exist_ok=True)
        sahne_video(plan, ses_yol[s["id"]], parca)
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
    print(f"video {CIKTI} {CIKTI.stat().st_size/1e6:.1f} MB {sure(CIKTI)/60:.2f} dk")


if __name__ == "__main__":
    main()
