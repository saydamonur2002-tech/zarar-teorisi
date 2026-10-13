#!/usr/bin/env python3
"""Etki cephesi anlatımı: HTML kare + Piper + ffmpeg.

Vekil ile ölçümü aynı cümlede toplamaz. Üç senaryo ucunun olasılık
ortalamasını yeni simülasyon diye okumaz. Kilitli CSV'lere yazmaz.
Ses: Piper tr_TR-dfki-medium. Model repoya girmez.
Çıktı: yayin/anlatim/etki_anlatim.mp4 ve .srt
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
HTML = (KOK / "etki.html").as_uri()
CIKTI = KOK / "etki_anlatim.mp4"
SRT = KOK / "etki_anlatim.srt"
ARA = Path("/tmp/anlatim-etki")
MODEL = Path("/tmp/piper-tr/tr_TR-dfki-medium.onnx")
MODEL_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/dfki/tr_TR-dfki-medium.onnx"
MODEL_JSON_URL = "https://huggingface.co/Derur/piper-tts-models/resolve/main/tr/dfki/tr_TR-dfki-medium.onnx.json"
UZUNLUK = 1.05
ARA_SAHNE = 0.25

SAHNELER = [
    {
        "id": "kapak",
        "baslik": "Fabrika",
        "metin": (
            "Bu video bir dünya köyünü anlatmaz. Bir fabrikayı anlatır. "
            "Köyde herkes aynı masada çay içer. Fabrikada katlar ayrıdır. "
            "Üst kat para, ölçü ve kural tutar. Bu kat bir ülke değildir. Bir havuzdur. "
            "Orta kat montaj yapar ve borcu çevirir. Türkiye, bu kurulumda orta kattadır. Yarı çevre denir. "
            "Alt kat hammadde ve ucuz emek verir. "
            "Modelin adı etki cephesidir. Artı değerin nereye aktığını bir tartıyla izler. "
            "Tartının adı vekildir. Vekil, ölçülmüş dolar değildir. Kasadaki banknotu saymaz. "
            "Kimin kefesinin ağır göründüğünü söyler. "
            "Ekranda yeşil damga ölçüdür. Kiremit damga vekildir. "
            "İkisini aynı cümlede toplamak, iki ayrı kefeyi tek sayı sanmaktır. "
            "Bir düşünün. Terazinin bir kefesine buğday, ötekine taş koyarsınız. "
            "İbre oynar. Oynayan ibre, buğdayın kilosu değildir. "
            "Önümüzdeki anlatı bu fabrikayı gezer. Dört lambayı ayrı ayrı yakar. "
            "Beş halkayı gösterir. İki kasayı ayırır. Havzaları, ülke masasını ve kurumları dizer. "
            "Üç yolu bir kaydırıcıyla tartar. On yılın sıfıra varmadığını söyler. "
            "Musluğu kapatmaz. Musluğun hangi katta durduğunu gösterir."
        ),
    },
    {
        "id": "kuram",
        "baslik": "Dört lamba",
        "metin": (
            "Dört lamba var. Birbirinin yerine geçmez. "
            "Birinci lamba Marx. Artı değer üretimde doğar. Finans onu yeniden böler. "
            "Yeni artı değer, bankadaki ücretli emek dışında, kasada doğmaz. "
            "İkinci lamba Wallerstein. Dünya bir köy değil, bir fabrikadır. "
            "Merkez finans ve standart tutar. Yarı çevre montaj ve borç servisi taşır. "
            "Çevre hammadde ve ucuz emek verir. "
            "Üçüncü lamba Minsky. Sağlam borç, borcu kendi gelirinden öder. "
            "Spekülatif borç, anaparayı çevirmek için yeni borç arar. "
            "Ponzi borç, faizi bile yeni borçla öder. "
            "Bu model, iki bin yirmi dört ile yirmi altı arasını ülke ölçeğinde spekülatif diye okur. "
            "Ponzi diye okumaz. Bir tarih vermez. Bir Minsky anı koymaz. "
            "Dördüncü lamba Polanyi. Para ve toprak, yani rant, ihale ve uzun sözleşme, "
            "piyasanın içinden çıkıp tahsisata döner. Fiyat gibi görünür. Kilit gibi durur. "
            "Doğru cümle şudur. Üretimdeki artı değer yetmez. Finansın payı onu aşar. Açık, dışarıdan kapanır. "
            "Yanlış cümle şudur. Finans kendi başına yeni artı değer yaratır. "
            "Dört lamba aynı odayı aydınlatır. Dört kapı açmaz. Biri, ötekinin kanıtı değildir."
        ),
    },
    {
        "id": "boru",
        "baslik": "Üç ağız",
        "metin": (
            "Fabrikadan çıkan boruyu üç ağızda düşünün. "
            "Yarı çevre boşalır. Beş halka bu boşalmayı taşır. Borunun ucu üçe ayrılır. "
            "Bir ağız merkeze sızar. Merkez burada bir harita parçası değildir. Bir finans havuzudur. "
            "İkinci ağız tampona ve koridora çarpar. Şok orada durur. "
            "Üçüncü ağız rakibin ikamesine gider. Başka bir montajcı aynı işi kapar. "
            "Bölgenin neti, bu üçüncü ağızdan, şokun ve dış bağın düşülmesidir. "
            "Rakip doldurursa havza toparlanır gibi görünür. "
            "Boru hâlâ dışarı akıyorsa, alıcı değişmiştir, sızıntı durmamıştır. "
            "Bunu bir musluk gibi düşünün. Kovayı başka bir odaya taşırsınız. "
            "Musluk aynı duvardadır. Su, yeni kovanın içine de akar. "
            "Çok kutupluluk bu yüzden tek başına bir teselli cümlesi değildir. "
            "Müşteri değişir. Musluk aynı yöne bakar. "
            "Havuzun kendisi de bir ülke tablosuna eşit bölünmez. "
            "Kalan merkez stoku, modelde belirsiz bir pay diye durur. Ölçülmüş bir alacak değildir. "
            "Havuz, haritadaki bir bayrak değildir. Sızıntının biriktiği kaptır. Kabı bir ülkeye yapıştırmak, suyu toprak sanmaktır."
        ),
    },
    {
        "id": "halka",
        "baslik": "Beş halka",
        "metin": (
            "Beş halka, otuz bir Ağustos iki bin yirmi altı tarihli tezde durur. "
            "Ağırlıklar modelin kendi terazisidir. Ölçülmüş pay değildir. "
            "Birinci halka üretim bağımlılığıdır. İthal girdi. Ağırlık sıfır virgül yirmi iki. "
            "İkinci halka mevzuat ve koordinasyon kopuşudur. Sıfır virgül on iki. En ince halka budur. "
            "Üçüncü halka yerel para sızıntısıdır. Rant ve faiz. Sıfır virgül yirmi. "
            "Dördüncü halka zararın bilançoya aktarımıdır. Sıfır virgül on sekiz. "
            "Beşinci halka dış kısıttır. Döviz, itibar, kefalet. Sıfır virgül yirmi sekiz. En kalın halka budur. "
            "Beşi birlikte bir eder. "
            "Bir bölge tamponsa, şok halkası kalınlaşır. Koridorsa, dış kısıt kalınlaşır. "
            "Rant havzasında para sızıntısı kalınlaşır. Montajda üretim bağımlılığı öne çıkar. "
            "Halkayı bir geminin bileziği gibi düşünün. Halat o bilezikten geçer. "
            "Bilezik, geminin kaderi değildir. Halatın hangi delikten çıktığının adıdır. "
            "Bu ağırlıklar bir yasa diye okunmaz. Modelin kendi terazisidir. "
            "Yüzde yüz, beş bileziğin paydasıdır. Bir bileziği kader diye okumak, halatı delikle karıştırmaktır."
        ),
    },
    {
        "id": "kasa",
        "baslik": "İki kasa",
        "metin": (
            "Şimdi iki kasa. Bu karedeki sayılar tezin ölçülmüş cümleleridir. Vekil değildir. "
            "Birinci kasa, firmanın firmayla olanıdır. "
            "İmalat ile ticaret arasında brüt on üç virgül dört trilyon liralık bir halka vardır. "
            "Net, artı kırk iki milyar liradır. Bu kasa kapanır. "
            "İkinci kasa, firmanın bankayla ve dövizle olanıdır. "
            "Reel sektörden bankalara on altı virgül sekiz trilyon lira yazılır. Bu kasa kapanmaz. "
            "Net döviz açığı, iki bin yirmi altı Haziranında iki yüz altı milyar dolardır. "
            "Öncesinde yüz kırk sekiz milyar dolar diye durur. "
            "İki bin yirmi dörtte faaliyet kârının yaklaşık yüzde seksen dördü finansmana gider. "
            "Ülke ölçeği spekülatiftir. Ponzi bandına yazılmamıştır. "
            "Enflasyonun sırası bu pencerede terstir. Yüksek lira faizi, döviz kredisini çağırır. Açık pozisyon büyür. "
            "Ödenmeyen zarar, fiyatların sebebi diye konmaz. İlerideki bir kur şokunun hammaddesi diye konur. "
            "İki kasayı tek kasa sanmak, kapanan halkayı kapanmayan açıklığın üstüne örtmektir. "
            "Dükkânda iki yazar kasa düşünün. Biri komşu dükkânla kapanır. Öteki bankanın kasasıyla açık kalır. "
            "Birinci fişi ikinci kasaya yapıştırmak, açığı kapatmaz."
        ),
    },
    {
        "id": "borc",
        "baslik": "Üç kişi",
        "metin": (
            "Masada üç kişi otursun. Biri üretim. Biri hane. Biri dış alacaklı. "
            "Üretim, henüz doğmamış bir artı değeri bugünden satar. Buna borç denir. "
            "Artı değer gelirse borç erir. Gelmezse fatura üç yere düşer. "
            "Hanenin alım gücüne. Kiraya, faize, sağlığa, eğitime. "
            "Kamunun kefaletine. Dış alacaklının kuruna. "
            "Borç üç yolla aşınır. Enflasyonla. Silinmeyle. Gerçek büyümeyle. "
            "Üçüncü yol, nisan metninde eksik kalmış olan yoldur. "
            "Tek kararla sıfırlanır demek, borcu musluktan değil afişten silmektir. "
            "Bir, iki ve üç aynı anda bitsin demek de tesisatı inkâr eder. Model tesisatın yanındadır. "
            "Londra hukuku, uzun imtiyaz sözleşmesi, hazine varsayımı. "
            "Bunlar yasal olarak kilitlenmiş bir rant aktarımıdır. "
            "Wallerstein’ın eşitsiz mübadele cümlesinin kendisi değildir. Akılcı bir körlüktür. "
            "Gören, sözleşmeyi görür. Görmeyen, onu piyasa fiyatı sanır. "
            "Üç kişiyi bir sofrada düşünün. Biri yarınki ekmeği bugünden satar. "
            "Ekmek pişmezse, fatura sofradakinin tabağına, evin kefiline ve dışarıdaki alacaklının defterine yazılır. "
            "Sofrayı bir sloganla kaldırmak, fırını çalıştırmaz."
        ),
    },
    {
        "id": "havza",
        "baslik": "İhracat",
        "metin": (
            "İhracat ölçüdür. İki bin yirmi dörtte toplam ihracat "
            "iki yüz altmış bir milyar dokuz yüz yirmi beş milyon dolardır. Ticaret istatistiği. "
            "Havzaların payı bu pastadan kesilir. "
            "En kalın dilim körfezdir. On milyar üç yüz on üç milyon dolar. Pastanın yüzde üç virgül dokuzu. "
            "Karadeniz dokuz milyar sekiz yüz altmış yedi milyon. Yüzde üç virgül sekiz. "
            "Irak’ın Bağdat hattı beş milyar sekiz yüz seksen milyon. Kuzey hattı dört milyar sekiz yüz on dokuz milyon. "
            "Bulgaristan dört milyar dört yüz üç milyon. Mısır üç milyar beş yüz yirmi üç milyon. "
            "Bu sütun yeşildir. Yanındaki vekil sütunu kiremittir. "
            "Körfez için vekil beştir. Bu beş, on milyar dolar demek değildir. "
            "Modelin kendi tartısındaki ağırlıktır. "
            "Haritayı gezerken yeşile bakıp kiremite dolar demeyin. "
            "Bunu bir pazarcı terazisi gibi düşünün. Sepetteki elmanın kilosu ölçüdür. "
            "Tezgahta asılı taş, satıcının o sepete biçtiği ağırlıktır. "
            "Taş, elmanın kendisi değildir. Havza, malın gittiği yerdir. Vekil, modelin o yere biçtiği ağırlıktır."
        ),
    },
    {
        "id": "harita",
        "baslik": "Havza neti",
        "metin": (
            "Bu harita katmanlı yolun makro havzalarıdır. Ekranda senaryo C diye durur. "
            "Sayılar vekildir. Dolar değildir. "
            "En derin eksi Ortadoğu’dadır. Fırat ve Doğu Akdeniz. Eksi bir virgül doksan iki. "
            "Kuzey Afrika eksi bir virgül kırk bir. Balkan eksi bir virgül on sekiz. "
            "Orta Asya eksi bir virgül on altı. Körfez eksi bir virgül on bir. "
            "Levant eksi sıfır virgül seksen sekiz. Karadeniz eksi sıfır virgül seksen üç. "
            "Kafkasya eksi sıfır virgül yetmiş. "
            "Hepsi eksidir. Havza, bu tartıda artı yazmaz. "
            "Çünkü net, rakibin doldurduğu işten, şokun, dış bağın ve rantın düşülmesidir. "
            "Körfezin ihracatı büyüktü. On milyar doların üstündeydi. O ölçüm yeşildi. "
            "Buradaki eksi bir virgül on bir, o doların kendisi değildir. Aynı havzanın, modeldeki net kefesidir. "
            "İran vekili ve Afrika boynu daha incedir. Dipnotta durur. "
            "Kalın ihracat, artı kefe demek değildir. Boru, mal gitsin diye susmaz."
        ),
    },
    {
        "id": "stok",
        "baslik": "Uluslararası defter",
        "metin": (
            "Uluslararası defter bir senaryoya bağlıdır. En olası yol, katmanlı oyundur. Refah katmanı açıktır. "
            "Bu karedeki sayılar vekildir. "
            "Türkiye eksi on yedi virgül iki. Merkez finans artı altı virgül bir. "
            "Çin artı üç virgül sekiz. İran artı bir virgül iki. "
            "Avrupa vekili artı bir virgül sıfır. Havza artı bir virgül dört. "
            "Bu altı satırı toplarsanız sıfır çıkmaz. Yaklaşık eksi üç virgül yedi kalır. "
            "Ekran bunu ayrıca yazar. Sıfır, bu altı satırın toplamı değildir. "
            "Sıfır, bütün matrisin kapanışıdır. Görünmeyen kefeler arayı kapatır. "
            "Bu bir keşif değildir. Matris, kapanacak biçimde kurulmuştur. "
            "Dünyanın muhasebesi sıfır çıktı diye okunmaz. "
            "Kurulan tartı, artıyı ve eksiği aynı kefeye koysun diye kurulmuştur. "
            "Havzanın brüt kayıp kenarı yüz kırk beş milyar doların üzerindedir. "
            "Bu kenar, stokla toplanmaz. Brüt, musluğun kalınlığıdır. Stok, kapta kalan sudur. "
            "Yanındaki dolar, havza köprüsünün çevirisidir. Üç köprüden biridir. "
            "Türkiye satırındaki eksi doksan iki buçuk milyar dolar, o köprünün cümlesidir. Tek cümle değildir. "
            "Balkan aktarımından sonra Avrupa’nın merkezde kalanı küçülür. Sırbistan bu tabloda eksiye yakındır."
        ),
    },
    {
        "id": "kurum",
        "baslik": "Ülke ve kurum",
        "metin": (
            "Masada otuz yedi ülke ve on kurum vardır. "
            "Kurumlar küçüktür. Ülkeler ve finans havuzu büyüktür. "
            "Sıranın başı merkez finanstır. Onu Çin ve Rusya izler. "
            "Sonra Amerika Birleşik Devletleri, İran ve Avrupa vekili gelir. "
            "Birleşik Arap Emirlikleri ve Suudi Arabistan rant havzası diye durur. Çubukları daha kısadır. "
            "Kurum tablosu sağdadır. En büyük kurum bile bir vekilin beşte birine varmaz. "
            "Uluslararası Para Fonu, Avrupa kurumları ve Dünya Bankası listenin başındadır. "
            "Listenin sonunda Dünya Ticaret Örgütü ve Birleşmiş Milletler vardır. "
            "Bu sıra, kurumun siyasi ağırlığı değildir. Modelin refah vekilindeki payıdır. "
            "Kurumun doları da vekildir. Ödenen aidat diye okunmaz. "
            "Çin’in artı kefesi, Türkiye’nin artı değerini cebine koyduğu ölçülmüş bir fatura değildir. "
            "Kalibre edilmiş bir kefedir. "
            "Bunu bir okul sırası gibi düşünün. Öndeki sıra, çocuğun boyudur. "
            "Müdürün makamı değildir. Sıra, tartının sırasıdır. "
            "Çubuğun rengi de hüküm değildir. Mavi havuzu, kiremit rakibi ayırır. İkisi de vekildir. İkisi de aidat değildir."
        ),
    },
    {
        "id": "senaryo",
        "baslik": "Üç yol",
        "qs": "",
        "metin": (
            "Üç yol var. Kaydırıcı onların ağırlığını taşır. Toplam yüzde yüzdür. "
            "A, atıl bağdır. Pasif tutum. Ağırlık yüzde yirmi iki. "
            "On yılın sonunda, yaşam katmanı dahil, bu ucun kendisi eksi on yedi virgül birdir. "
            "B, araçsallaşma ve donmuş düğümdür. Ağırlık yüzde on sekiz. "
            "Bu ucun kendisi eksi otuz iki virgül yedidir. "
            "C, katmanlı oyundur. Kısmi kullanım. En olası yol. Ağırlık yüzde altmış. "
            "Bu ucun kendisi eksi on bir virgül yedidir. "
            "Soldaki büyük sayı karışımdır. Eksi on altı virgül yedi. "
            "Sağdaki üç sayı, ucun kendisidir. Karışım, ucun yerine geçmez. "
            "Katmanlı yolun payı yüksek olduğu için beklenen, ona yakındır. "
            "Araçsal yolun payı küçük olduğu için onun derin eksiği ortalamayı dibe çekmez. "
            "Bu ağırlıklar ölçülmüş ihtimal değildir. Modelin kendi senaryo tartısıdır. "
            "Ara ağırlık, üç yayınlanmış ucun ortalamasıdır. Yeni bir simülasyon değildir. "
            "Kaydırıcıyı oynatmak dünyayı değiştirmez. Tartının varsayımını değiştirir. "
            "Ekrandaki yüzde yirmi iki, yüzde on sekiz ve yüzde altmış, bu karenin varsayılanıdır. "
            "Kaydırıcıyı oynatınca uçlar yerinde kalır. Yalnız soldaki büyük sayı yürür."
        ),
    },
    {
        "id": "senaryob",
        "baslik": "Ağırlık B",
        "kare": "senaryo",
        "qs": "pa=10&pb=50&pc=40",
        "metin": (
            "Kaydırıcıyı araçsal yola yatırıyorum. A yüzde on. B yüzde elli. C yüzde kırk. "
            "Toplam yine yüzde yüz. "
            "Soldaki büyük sayı eksi yirmi iki virgül yediye iner. "
            "Sağdaki uçlar yerinde durur. Araçsal yolun kendi ucu hâlâ eksi otuz iki virgül yedidir. "
            "Karışım, ucun kendisi değildir. "
            "B, borunun araçsallaştığı yoldur. Bağ, dar bir çıkar ağına döner. "
            "Merkez sızıntısının çarpanı bir virgül on beşe çıkar. "
            "Levant düğümü bir virgül otuz beşle kalınlaşır. "
            "Diplomatik esneklik eksiye döner. "
            "Bu kare, dünyanın böyle olacağını söylemez. "
            "Ağırlığı araçsal yola verince tartının ne gösterdiğini söyler. "
            "C hâlâ yüzde kırktır. En olası yol bütünüyle silinmemiştir. "
            "Yine de ortalama, katmanlı yolun kendi eksi on bir virgül yedisinden belirgin biçimde daha derindir. "
            "Bunu bir tartıya konan üç taş gibi düşünün. "
            "Ortadaki taşı ağırlaştırırsınız. İbre ortaya kayar. Taşların kendi ağırlığı değişmez. "
            "Ekranda A on, B elli, C kırk yazar. Büyük sayı eksi yirmi iki virgül yedidir. Uçlar eski yerindedir."
        ),
    },
    {
        "id": "senaryoc",
        "baslik": "Ağırlık C",
        "kare": "senaryo",
        "qs": "pa=10&pb=10&pc=80",
        "metin": (
            "Kaydırıcıyı katmanlı yolda bırakıyorum. A yüzde on. B yüzde on. C yüzde seksen. "
            "Soldaki büyük sayı eksi on dört virgül üçtür. "
            "Katmanlı yolun kendi ucu eksi on bir virgül yediydi. Yüzde seksenlik pay, ortalamayı oraya yaklaştırır. "
            "Tam üstüne oturtmaz. Çünkü A ve B hâlâ yüzde onar ağırlık taşır. "
            "Modelin kendi varsayılanı bu değildir. "
            "Varsayılan, yüzde yirmi iki, yüzde on sekiz ve yüzde altmıştır. "
            "O tartı eksi on altı virgül yedi veriyordu. "
            "Burada katmanlı yolu şişirdik. İyileşme gibi görünen fark, politikanın başarısı değildir. "
            "Ağırlığın yer değiştirmesidir. "
            "Kapı skoru kaydırıcıyla oynamaz. Ekranın altındaki sayılar sabittir. "
            "Bütün altmış altı virgül dört. C yolu yetmiş bir virgül üç. "
            "Varsayılan karışım elli yedi virgül üç. "
            "Bu skor, dünyanın gerçekleşme ihtimali değildir. Modelin kendi iç kapısıdır. "
            "Kapıyı dünya sanmak, tartıyı hava durumu sanmaktır. "
            "Ekranda A on, B on, C seksen yazar. Büyük sayı eksi on dört virgül üçtür. "
            "Alttaki altmış altı virgül dört, yetmiş bir virgül üç ve elli yedi virgül üç yerinden oynamaz."
        ),
    },
    {
        "id": "yol",
        "baslik": "On yıl",
        "metin": (
            "On yıl, iki bin yirmi yedi ile iki bin otuz altı arasındadır. "
            "Kalibre edilmiş C yolu. Refah katmanı açık. "
            "Türkiye’nin neti eksi on yedi virgül ikiden başlar. "
            "Onuncu yılda eksi on iki virgül beşe gelir. "
            "İyileşme dört virgül yedi vekildir. Sıfıra çıkmaz. Çizginin üstünde boşluk vardır. Sıfır oradadır, çerçevenin dışında. "
            "Milli gelire oran, orta köprüde yüzde dört virgül sekizden yüzde üç virgül beşe iner. "
            "Yaklaşık bir virgül üç puan. Bu, büyüme tahmini değildir. "
            "Yapısal sürüklenmenin milli gelire oranıdır. "
            "İlk yıllar zarar fazıdır. İki bin otuz üç ve otuz dört düzleşir. "
            "Otuz beş ve otuz altıda üretim fazı başlar. "
            "Finans fazının tamamı, modelin kendi vekiliyle, iki bin elli yediye uzar. "
            "On yıl, paketin bitişi değildir. Kısmi bir incelmedir. "
            "Üç kutu ayrıdır. Onları toplamayın. "
            "Ham tartı, finans katmanının sonunda artı sıfır virgül yetmiş beş vekil gösteriyordu. "
            "Kalibrasyon o katmanı eksi on virgül bire çeker. "
            "Yayınlanan on yıl yolu ise refah katmanı açıkken eksi on yedi virgül ikiden başlar. "
            "Artı işaret, ham tartının cümlesidir. Yayınlanan yol, eksi işaretli kalibre yoldur."
        ),
    },
    {
        "id": "kopru",
        "baslik": "Üç köprü",
        "metin": (
            "Aynı vekili üç köprüden geçirmek, üç ayrı cümle kurar. "
            "Bir vekil, ödemeler dengesi köprüsünde yaklaşık iki bin seksen sekiz milyon dolar eder. "
            "Havza köprüsünde yaklaşık beş bin üç yüz seksen üç milyon dolar eder. "
            "Mal ticareti köprüsünde yaklaşık dört bin yedi yüz seksen beş milyon dolar eder. "
            "Türkiye’nin eksi on yedi virgül iki vekili, birinci köprüde otuz beş virgül dokuz milyar dolar, "
            "ikinci köprüde doksan iki virgül beş milyar dolar, "
            "üçüncü köprüde seksen iki virgül üç milyar dolar gibi durur. "
            "Ortadaki geometrik ortalama altmış dört virgül dokuz milyar dolardır. "
            "Milli gelir oranı bu ortayla kurulur. "
            "Dört sayıdan birini seçmek bir tercihtir. Dördünü toplamak, aynı kefeyi dört kez saymaktır. "
            "Ölçülmüş çapa ayrıdır. İki bin yirmi dörtte yatırım geliri gideri on sekiz virgül sekiz milyar dolardır. "
            "Modelin merkez finans kenarı aynı yılda on bir virgül sekiz milyar dolar verir. Eşit değildir. Yakınlık, özdeşlik değildir. "
            "Net ticaret eksi seksen iki virgül iki milyar dolardır. Mal köprüsü bu satıra bakar. "
            "Milli gelir çapası bir trilyon üç yüz elli altı milyar dolar vekilidir. "
            "Oran, kaybın buna bölümüdür. Büyümenin kendisi değildir."
        ),
    },
    {
        "id": "sinir",
        "baslik": "Sınır",
        "metin": (
            "Son kare bir sınır listesidir. "
            "Model, emperyalizmi kanıtlamaz. Bağıntı, neden değildir. "
            "Vekil, ölçülmüş alacak değildir. "
            "Defterin sıfıra kapanması, dünyanın sıfırlandığı anlamına gelmez. Matris öyle kurulmuştur. "
            "Çin’in artı kefesi, Türkiye’den tahsil edilmiş bir fatura değildir. "
            "Minsky anı için bir tarih yoktur. Ülke spekülatif bantta okunur. Ponzi diye damgalanmaz. "
            "Üç senaryo bir reçete değildir. Kaydırıcı bir politika düğmesi değildir. "
            "On yıl sıfıra varmaz. Ham modelin artı işareti yayınlanan sonuç değildir. "
            "Üç köprü toplanmaz. Beş halka bir kader yasası değildir. Ağırlıktır. "
            "Yan depodaki zarar teorisi içerideki defteri sayar. Bu tartı dışarıdaki boruyu sayar. İkisi toplanmaz. "
            "Ölçülmüş cümle azdır ve değerlidir. İki bin yirmi dört ihracatı. Yatırım geliri gideri. Net ticaret. "
            "Faaliyet kârının finansmana giden payı. Net döviz açığı. "
            "Bunların dışında gördüğünüz tartı, vekildir. "
            "Fabrika ayaktadır. Boru akmaktadır. Alıcı değişebilir. "
            "Musluk, alıcı değişince kendi kendine kapanmaz. "
            "Bu video o musluğu kapatmaz. Musluğun hangi katta, hangi kefede durduğunu gösterir."
        ),
    },
]


def _url(sahne: dict) -> str:
    url = HTML + "?kare=" + sahne.get("kare", sahne["id"])
    if sahne.get("qs"):
        url += "&" + sahne["qs"]
    return url


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
    sozcuk = sum(len(s["metin"].split()) for s in SAHNELER)
    print(f"sözcük {sozcuk}")
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
    if not (1080 <= toplam <= 1320):
        raise SystemExit(f"süre bandın dışında: {toplam:.0f} sn")
    print("kare")
    (ARA / "kare").mkdir()

    def bir(s):
        yol = ARA / "kare" / f"{s['id']}.png"
        cek(_url(s), yol)
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
