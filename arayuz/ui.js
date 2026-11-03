"use strict";

(function () {
  const veri = JSON.parse(document.getElementById("veri").textContent);
  const AD = { dusuk: "düşük", orta: "orta", yuksek: "yüksek" };
  const HUKUM = { yanlis: "yanlış", ayakta: "ayakta", ayakta_degil: "ayakta değil" };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function tr(x, n) {
    if (x === null || x === undefined || Number.isNaN(x)) return "—";
    const neg = x < 0;
    const s = Math.abs(x).toFixed(n);
    const parca = s.split(".");
    const tam = parca[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return (neg ? "−" : "") + tam + (parca[1] ? "," + parca[1] : "");
  }

  function sinif(etiket) {
    return etiket === "kanıt" ? "kanit" : "aday";
  }

  function rakam(deger, opt) {
    const n = opt.ondalik === undefined ? 4 : opt.ondalik;
    const birim = opt.birim ? '<span class="birim">' + esc(opt.birim) + "</span>" : "";
    const href = "../" + opt.kaynak;
    return (
      '<span class="rakam"><span class="deger">' + tr(deger, n) + "</span>" + birim +
      ' <a class="kaynak" href="' + esc(href) + '">' + esc(opt.kaynak.split("/").pop()) + "</a>" +
      ' <span class="rozet ' + sinif(opt.etiket) + '">' + esc(opt.etiket) + "</span></span>"
    );
  }

  function hucre(ad, deger, opt) {
    return "<tr><th>" + esc(ad) + "</th><td>" + rakam(deger, opt) + "</td></tr>";
  }

  function tablo(satirlar) {
    return '<div class="tablo-kaydir"><table><tbody>' + satirlar + "</tbody></table></div>";
  }

  function grafikCubuk(satirlar, baslik) {
    const w = 640;
    const h = 200;
    const vals = satirlar.map(function (s) { return s.deger; }).concat([0]);
    const min = Math.min.apply(null, vals);
    const max = Math.max.apply(null, vals);
    const span = max - min || 1;
    const y0 = 16;
    const y1 = 164;
    function y(v) { return y1 - ((v - min) / span) * (y1 - y0); }
    const bw = 600 / satirlar.length;
    let ciz = '<line x1="28" y1="' + y(0) + '" x2="628" y2="' + y(0) + '" stroke="#1c1915"/>';
    satirlar.forEach(function (s, i) {
      const x = 36 + i * bw;
      const top = Math.min(y(s.deger), y(0));
      const height = Math.max(1, Math.abs(y(s.deger) - y(0)));
      ciz += '<rect x="' + x + '" y="' + top + '" width="' + (bw * 0.55) + '" height="' + height + '" fill="' + (s.renk || "#1f4d3a") + '"/>';
      ciz += '<text x="' + (x + bw * 0.28) + '" y="186" text-anchor="middle" font-size="12" fill="#1c1915">' + esc(s.ad) + "</text>";
    });
    return '<figure><figcaption>' + esc(baslik) + '</figcaption><svg viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(baslik) + '">' + ciz + "</svg></figure>";
  }

  function grafikBant(satirlar, baslik) {
    const w = 640;
    const h = 210;
    const vals = [0];
    satirlar.forEach(function (s) { vals.push(s.lo, s.hi); });
    const min = Math.min.apply(null, vals);
    const max = Math.max.apply(null, vals);
    const span = max - min || 1;
    const y0 = 16;
    const y1 = 168;
    function y(v) { return y1 - ((v - min) / span) * (y1 - y0); }
    const bw = 600 / satirlar.length;
    let ciz = '<line x1="28" y1="' + y(0) + '" x2="628" y2="' + y(0) + '" stroke="#1c1915"/>';
    satirlar.forEach(function (s, i) {
      const x = 40 + i * bw;
      const top = Math.min(y(s.lo), y(s.hi));
      const height = Math.max(2, Math.abs(y(s.hi) - y(s.lo)));
      ciz += '<rect x="' + x + '" y="' + top + '" width="' + (bw * 0.45) + '" height="' + height + '" fill="#3d5a4c"/>';
      ciz += '<text x="' + (x + bw * 0.22) + '" y="192" text-anchor="middle" font-size="12" fill="#1c1915">' + esc(s.ad) + "</text>";
    });
    return '<figure><figcaption>' + esc(baslik) + '</figcaption><svg viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(baslik) + '">' + ciz + "</svg></figure>";
  }

  function oku() {
    const ad = document.querySelector("#secici button[data-ad][aria-pressed='true']").getAttribute("data-ad");
    const beta = Number(document.querySelector("#secici button[data-beta][aria-pressed='true']").getAttribute("data-beta"));
    const theta = Number(document.getElementById("theta").value);
    const chi = Number(document.getElementById("chi").value);
    return { ad: ad, theta: theta, chi: chi, beta: beta };
  }

  function adimlariYaz() {
    const m = veri.m2;
    const my = m.m2.milyar;
    const ay = m.adim12.birlesik;
    const json = "para_arzi/m2_etki.json";
    const kart = [
      {
        no: "1",
        baslik: "Stok üst sınırı",
        tanim: "Kimden kime stokta üst sınır. Silinen sütun boştur; tavan bir skor değildir.",
        girdi: "EVDS stokları ve metindeki ters bacak. Kimden-kime xls depoda yoktur.",
        cikti: [
          ["eski tavan", 0.0728, 4, "", "BES_ADIM.md", "kanıt"],
          ["yeni tavan", 0.2582, 4, "", "BES_ADIM.md", "kanıt"],
          ["araç ayrı, M2", m.adim12.ayri.m2, 1, "milyar TL", json, "kanıt"],
          ["birleşik yurt içi ayak", ay.m2_aday, 1, "milyar TL", json, "aday"],
          ["birleşik silinen", ay.silinen, 1, "milyar TL", json, "kanıt"],
          ["yurt dışı mevduat ayağı", ay.mevduat_ayak_yurtdisi, 1, "milyar TL", json, "kanıt"],
        ],
      },
      {
        no: "2",
        baslik: "Akış mahsubu",
        tanim: "Net pozisyonu sabit tutan akış oranı. Mevduat stoku bu adımdan çıkmaz.",
        girdi: "Mahsup oranı ve adım 2 parametreleri. λ* kalibrasyondur, M2 girdisi değildir.",
        cikti: [
          ["mahsup oranı", 0.421, 3, "", "para_arzi/M2_ETKI.md", "kanıt"],
          ["mahsup, M2", m.adim12.mahsup_0421.m2, 1, "milyar TL", json, "kanıt"],
          ["λ*", 0.8931, 4, "", "ADIM2_NACE_AG.md", "aday"],
          ["β tavanı", 0.0439, 4, "", "ADIM2_NACE_AG.md", "aday"],
        ],
      },
      {
        no: "3",
        baslik: "Faiz durması",
        tanim: "I = ψ · (r/4) · D ve D = κ · u2 · S0. Anapara ve mevduat stoku düşmez. r son gözlemde donar.",
        girdi: "S0 firma F.4 stoku, ψ ölçüm türevi, r ticari faiz, κ senaryoya kilitli varsayım.",
        cikti: [
          ["S0", 25339.8, 1, "milyar TL", "ADIM3_FAIZ_DURMA.md", "kanıt"],
          ["ψ", 0.3584, 4, "", "ADIM3_FAIZ_DURMA.md", "aday"],
          ["r, son gözlem", veri.reel.i0, 4, "%", "para_arzi/REEL_RAHATLAMA.md", "kanıt"],
          ["doğrudan M2", m.adim345.adim3, 1, "milyar TL", json, "kanıt"],
        ],
      },
      {
        no: "4",
        baslik: "Adres mevduatı senede",
        tanim: "Tepe = θ × adres. Kalıcı = χ × tepe. Vade 8 çeyrek. Kredi itişi = eldeki stok × 0,08, yıllık akıştır, stoka eklenmez.",
        girdi: "Adres, örtüşme bandı. θ ve χ seçicidedir. Ham toplam ile örtüşme sonrası adres ayrıdır.",
        cikti: [
          ["hane vadeli", 8322.4, 1, "milyar TL", "ADIM4_ADRES_YONLENDIRME.md", "kanıt"],
          ["firma vadeli", 4400.1, 1, "milyar TL", "ADIM4_ADRES_YONLENDIRME.md", "kanıt"],
          ["gerçek kişi YP", ZT.GERCEK_YP, 1, "milyar TL", "ADIM4_ADRES_YONLENDIRME.md", "kanıt"],
          ["düşük adres", m.senaryo[0].adres, 1, "milyar TL", json, "kanıt"],
          ["orta ve yüksek adres", m.senaryo[1].adres, 1, "milyar TL", json, "kanıt"],
          ["kredi payı", ZT.KREDI_PAY, 2, "", "para_arzi/m2_etki.py", "aday"],
        ],
      },
      {
        no: "4.5",
        baslik: "Yeni birim, λ = 1",
        tanim: "Plasebo. TL stok λ ile ölçeklenir; λ = 1 iken stok durur. USD stoku ve faiz durur. Kur sabittir.",
        girdi: "2026-Q1 TL para stoku. Bu stok M2 değildir.",
        cikti: [
          ["λ", 1, 0, "", "ADIM45_BIRIM.md", "aday"],
          ["kur", 49.1274, 4, "TL/USD", "para_arzi/ENFLASYON_ETKI.md", "kanıt"],
          ["TL stok, λ = 1", m.tl_para_stoku.tl_para_stoku, 1, "milyar TL", "ADIM45_BIRIM.md", "kanıt"],
          ["doğrudan M2", m.adim345.adim45, 1, "milyar TL", json, "kanıt"],
          ["yürütme A alt", 0.59, 2, "milyar TL", "BES_ADIM.md", "aday"],
          ["yürütme A üst", 5.4, 2, "milyar TL", "BES_ADIM.md", "aday"],
          ["yürütme B alt", 189.7, 1, "milyar TL", "BES_ADIM.md", "aday"],
          ["yürütme B üst", 632.4, 1, "milyar TL", "BES_ADIM.md", "aday"],
        ],
      },
      {
        no: "5",
        baslik: "Kira, Ho → Ha",
        tanim: "İki hane arasında aktarım. Yıl adım 5 dosyasında yoktur. Doğrudan M2 sıfırdır. Kira puanı enflasyon tablosuna yazılmaz.",
        girdi: "Birim kira ve HEKİS havuz kirası. Alan ve kiracı payı varsayımdır.",
        cikti: [
          ["birim kira", 275.37, 2, "TL/m²/ay", "ADIM5_KIRA.md", "kanıt"],
          ["HEKİS havuz", 20000, 0, "TL/ay", "BES_ADIM.md", "aday"],
          ["yol A alt", 2005.8, 1, "milyar TL/yıl", "ADIM5_KIRA.md", "aday"],
          ["yol A üst", 2941.8, 1, "milyar TL/yıl", "ADIM5_KIRA.md", "aday"],
          ["yol B vekil", 254.8, 1, "milyar TL/yıl", "ADIM5_KIRA.md", "aday"],
          ["doğrudan M2", m.adim345.adim5, 1, "milyar TL", json, "kanıt"],
        ],
      },
    ];
    const kok = document.querySelector("#adimlar .kartlar");
    kok.innerHTML = kart.map(function (k) {
      const satir = k.cikti.map(function (c) {
        return hucre(c[0], c[1], { ondalik: c[2], birim: c[3], kaynak: c[4], etiket: c[5] });
      }).join("");
      return (
        "<article><h3>Adım " + esc(k.no) + " — " + esc(k.baslik) + "</h3>" +
        "<p><strong>Tanım.</strong> " + esc(k.tanim) + "</p>" +
        "<p><strong>Girdi.</strong> " + esc(k.girdi) + "</p>" +
        "<p><strong>Çıktı.</strong></p>" + tablo(satir) + "</article>"
      );
    }).join("");
    kok.insertAdjacentHTML("afterend",
      "<p>M2 düzeyi " + rakam(my.m2, { ondalik: 4, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      ", hafta " + esc(m.hafta) + ". Menkul " +
      rakam(my.menkul, { ondalik: 4, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      " M2 dışındadır. DİBS " +
      rakam(m.dibs_milyar, { ondalik: 1, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      " menkul satırı değildir.</p>"
    );
  }

  function m2Yaz(c) {
    const json = "para_arzi/m2_etki.json";
    const py = "para_arzi/m2_etki.py";
    const my = veri.m2.m2.milyar;
    const kanit = { kaynak: json, etiket: "kanıt" };
    const aday = { kaynak: py, etiket: "aday" };
    const s = c.m2;
    const govde = c.govde.adim12 === 0 ? "kanıt" : "aday";
    const govdeKaynak = c.govde.adim12 === 0 ? json : json;
    let html = "<h3>Düzey, " + esc(veri.m2.hafta) + "</h3>" + tablo(
      hucre("dolaşım", my.dolasim, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("vadesiz TL", my.vadesiz_tl, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("vadeli TL", my.vadeli_tl, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("vadesiz YP", my.vadesiz_yp, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("vadeli YP", my.vadeli_yp, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("M2", my.m2, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit)) +
      hucre("M3", my.m3, Object.assign({ ondalik: 4, birim: "milyar TL" }, kanit))
    );
    html += "<h3>Seçili senaryo</h3><p>Adres " +
      rakam(c.govde.adres, { ondalik: 1, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      ", κ " + rakam(c.govde.kappa, { ondalik: 2, kaynak: "para_arzi/reel_rahatlama.py", etiket: "aday" }) +
      ". İkinci tur stok toplamına girmez.</p>";
    html += tablo(
      hucre("adım 1–2", s.adim12_m2, { ondalik: 4, birim: "milyar TL", kaynak: govdeKaynak, etiket: govde }) +
      hucre("adım 3", s.adim3_m2, { ondalik: 1, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      hucre("adım 4 tepe", s.adim4_tepe, Object.assign({ ondalik: 4, birim: "milyar TL" }, aday)) +
      hucre("adım 4 kalıcı", s.adim4_kalici, Object.assign({ ondalik: 4, birim: "milyar TL" }, aday)) +
      hucre("adım 4.5", s.adim45_m2, { ondalik: 1, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      hucre("adım 5", s.adim5_m2, { ondalik: 1, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      hucre("başlık stok", s.baslik_stok, Object.assign({ ondalik: 4, birim: "milyar TL" }, aday)) +
      hucre("başlık / M2", s.baslik_yuzde, Object.assign({ ondalik: 4, birim: "%" }, aday)) +
      hucre("tepe stok", s.tepe_stok, Object.assign({ ondalik: 4, birim: "milyar TL" }, aday)) +
      hucre("tepe / M2", s.tepe_yuzde, Object.assign({ ondalik: 4, birim: "%" }, aday)) +
      hucre("2. tur tepe", s.ikinci_tur_tepe_yillik, Object.assign({ ondalik: 4, birim: "milyar TL/yıl" }, aday)) +
      hucre("2. tur kalıcı", s.ikinci_tur_kalici_yillik, Object.assign({ ondalik: 4, birim: "milyar TL/yıl" }, aday))
    );
    html += grafikCubuk([
      { ad: "tepe", deger: s.adim4_tepe },
      { ad: "kalıcı", deger: s.adim4_kalici },
      { ad: "başlık", deger: s.baslik_stok },
    ], "M2 stok düşüşü, milyar TL. Tepe başlığa girmez.");
    const bol = document.getElementById("m2");
    bol.querySelectorAll(":scope > :not(h2)").forEach(function (n) { n.remove(); });
    bol.insertAdjacentHTML("beforeend", html);
  }

  function enflasyonYaz(c) {
    const ej = "para_arzi/enflasyon_etki.json";
    const py = "para_arzi/enflasyon_etki.py";
    const p = veri.enf.para;
    const b = veri.enf.birlesik_2028;
    let html = "<blockquote>Modelde enflasyon dışsaldır; bu hesap model dışı bir köprüdür, sonuç modele geri beslenmez.</blockquote>";
    html += "<p>Kaynak <a href=\"../para_arzi/ENFLASYON_ETKI.md\">ENFLASYON_ETKI.md</a>. " +
      "r " + rakam(veri.reel.i0, { ondalik: 4, birim: "%", kaynak: "para_arzi/ENFLASYON_ETKI.md", etiket: "kanıt" }) +
      " ve kur " + rakam(49.1274, { ondalik: 4, kaynak: "para_arzi/ENFLASYON_ETKI.md", etiket: "kanıt" }) +
      " beş adımın çıktısına bağlanmaz.</p>";
    html += "<p>Örneklemde Δlog M2 " +
      rakam(p.dlog_m2_min, { ondalik: 4, kaynak: ej, etiket: "aday" }) + " ile " +
      rakam(p.dlog_m2_max, { ondalik: 4, kaynak: ej, etiket: "aday" }) +
      " arasındadır; ikisi de artıştır. Daralma bu örneklemin dışındadır. b1 " +
      rakam(p.b1.nokta, { ondalik: 4, kaynak: ej, etiket: "aday" }) + ", b2 " +
      rakam(p.b2.nokta, { ondalik: 4, kaynak: ej, etiket: "aday" }) +
      ". Kur kanalı tahmin edilemedi (n = " + rakam(veri.enf.kur_model.n, { ondalik: 0, kaynak: ej, etiket: "aday" }) +
      "); skorlanan kur puanı " + rakam(0, { ondalik: 0, birim: "puan", kaynak: py, etiket: "aday" }) + ".</p>";
    html += "<p>Birleşik ayak " + rakam(b.dm2, { ondalik: 1, birim: "milyar TL", kaynak: ej, etiket: "aday" }) +
      " 2028 para puanı " + rakam(b.nokta, { ondalik: 2, birim: "puan", kaynak: ej, etiket: "aday" }) +
      ". Skora girmez. Büyüme noktasının katsayısı sıfırı içerdiği için büyüme puanı " +
      rakam(c.enf.buyume.tepe, { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" }) +
      " (tepe) ve " + rakam(c.enf.buyume.kalici, { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" }) +
      " (kalıcı). Enflasyon toplamına yazılmaz.</p>";
    if (c.enf.hiz_tepe !== 0) {
      html += '<p class="uyari">Para puanı, stokun düştüğü yılın geçişidir. Hız özdeşliği ' +
        rakam(c.enf.hiz_tepe, { ondalik: 4, kaynak: py, etiket: "kanıt" }) +
        " fiyat denklemine eklenmez.</p>";
    }
    const baslik = "<tr><th>Yıl</th><th>Para alt</th><th>Para üst</th><th>Maliyet α=1</th><th>Kredi</th><th>Toplam</th><th>Kredi hariç</th></tr>";
    const bantlar = [];
    let govde = "";
    ZT.YILLAR.forEach(function (yil) {
      const h = c.enf.yil[yil];
      const opt = { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" };
      govde += "<tr><th>" + yil + "</th><td>" + rakam(h.para_alt, opt) + "</td><td>" + rakam(h.para_ust, opt) +
        "</td><td>" + rakam(h.maliyet[1], opt) + "</td><td>" + rakam(h.kredi, opt) +
        "</td><td>" + rakam(h.toplam[0], opt) + " … " + rakam(h.toplam[1], opt) +
        "</td><td>" + rakam(h.toplam_kredisiz[0], opt) + " … " + rakam(h.toplam_kredisiz[1], opt) + "</td></tr>";
      bantlar.push({ ad: yil, lo: h.toplam[0], hi: h.toplam[1] });
    });
    html += '<div class="tablo-kaydir"><table><thead>' + baslik + "</thead><tbody>" + govde + "</tbody></table></div>";
    html += "<p>Kira, yıl yok: " +
      rakam(c.enf.kira[0], { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" }) + " … " +
      rakam(c.enf.kira[1], { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" }) +
      ". Kapsama " + rakam(c.govde.kapsam, { ondalik: 2, kaynak: "para_arzi/enflasyon_etki.py", etiket: "aday" }) +
      ", ağırlık " + rakam(ZT.KIRA_W, { ondalik: 6, kaynak: "para_arzi/enflasyon_etki.py", etiket: "aday" }) + ".</p>";
    html += grafikBant(bantlar, "Yıllık TÜFE puanı, kredi dahil toplamın iki ucu. Eksi, o yıl daha yavaş artıştır.");
    const bol = document.getElementById("enflasyon");
    bol.querySelectorAll(":scope > :not(h2)").forEach(function (n) { n.remove(); });
    bol.insertAdjacentHTML("beforeend", html);
  }

  function isaret(h) {
    const d = [];
    if (h.tanim_disi) d.push("tanım dışı");
    if (!h.hukme_girer && h.delta_pi > 0) d.push("artış");
    if (h.delta_pi === 0) d.push("sapma yok");
    if (h.taban_bagli) d.push("taban 0");
    if (!d.length) d.push("tanım içi");
    return d.join(", ");
  }

  function reelYaz(c) {
    const py = "para_arzi/reel_rahatlama.py";
    const md = "para_arzi/REEL_RAHATLAMA.md";
    let html = "<blockquote>" + esc(veri.reel.cumle) + "</blockquote>";
    html += "<p>Kilitli üç senaryonun birlikte hükmü: <strong>" + esc(HUKUM[veri.reel.hukum.hukum] || veri.reel.hukum.hukum) + "</strong>. " +
      "Kaynak <a href=\"../" + md + "\">REEL_RAHATLAMA.md</a>. " +
      "i(β) = max(0, i₀ + β·Δπ). Nominal taban 0'dır. Net = I(β)/(1+(π₀+Δπ)/100) − I₀/(1+π₀/100).</p>";
    html += "<p>I₀ " + rakam(c.govde.I, { ondalik: 1, birim: "milyar TL", kaynak: "para_arzi/enflasyon_etki.json", etiket: "aday" }) +
      ", π₀ " + rakam(veri.reel.pi0, { ondalik: 2, birim: "%", kaynak: md, etiket: "kanıt" }) +
      ", seçili β " + rakam(c.beta, { ondalik: 1, kaynak: py, etiket: "aday" }) + ".</p>";
    let bas = "<tr><th>Yıl</th><th>Δπ</th><th>i</th><th>Nominal</th><th>Fazlalık</th><th>Reel</th><th>Net</th><th>İşaret</th></tr>";
    const cubuk = [];
    ["2029", "2030", "2031"].forEach(function (yil) {
      c.reel[yil].forEach(function (uclar, i) {
        const h = uclar.filter(function (x) { return x.beta === c.beta; })[0];
        const opt = { ondalik: 2, birim: "milyar TL", kaynak: py, etiket: "aday" };
        const cls = h.tanim_disi ? ' class="uyari"' : "";
        bas += "<tr" + cls + "><th>" + yil + "</th><td>" +
          rakam(h.delta_pi, { ondalik: 2, birim: "puan", kaynak: py, etiket: "aday" }) + "</td><td>" +
          rakam(h.i, { ondalik: 2, birim: "%", kaynak: py, etiket: "aday" }) + "</td><td>" +
          rakam(h.nominal, opt) + "</td><td>" + rakam(h.fazlalik, opt) + "</td><td>" +
          rakam(h.reel, opt) + "</td><td>" + rakam(h.net, opt) + "</td><td>" + esc(isaret(h)) + "</td></tr>";
        cubuk.push({
          ad: yil + (i === 0 ? " alt" : " üst"),
          deger: h.net,
          renk: h.net < 0 ? "#8c3b2a" : "#1f4d3a",
        });
      });
    });
    html += '<div class="tablo-kaydir"><table>' + bas + "</table></div>";
    html += "<p>Net pozitifse sabit tablo reel rahatlamayı küçük yazar. Net negatifse tablo büyük yazar. Tanım dışı hücre hükme girmez.</p>";
    html += grafikCubuk(cubuk, "Seçili β için net reel rahatlama, milyar TL. İki uç, o yılın toplam bandıdır.");
    const bol = document.getElementById("reel");
    bol.querySelectorAll(":scope > :not(h2)").forEach(function (n) { n.remove(); });
    bol.insertAdjacentHTML("beforeend", html);
  }

  function rantYaz() {
    const r = veri.rant;
    const e = veri.etki;
    const rj = "rant_aktor_sonuc.json";
    const md = e.kaynak;
    let html = "<p>Mevcut senaryoda yıllık rant baseline'da durur. Dosya durumu «" + esc(r.durum) +
      "», ölçüm değil. Rozet adaydır.</p>";
    let satir = "";
    Object.keys(r.baseline).forEach(function (aktor) {
      satir += hucre(aktor + " baseline", r.baseline[aktor], { ondalik: 2, birim: "milyar TL/yıl", kaynak: rj, etiket: "aday" });
      satir += hucre(aktor + " mevcut kayıp", r.kayip[aktor], { ondalik: 1, birim: "milyar TL", kaynak: rj, etiket: "aday" });
    });
    html += tablo(satir);
    html += "<h3>Etki cephesi, K1 sonrası</h3><p>Güncel SFC satırı bu bölümdür. K1 öncesi Σ " +
      rakam(e.once_sigma, { ondalik: 3, birim: "trilyon TL", kaynak: md, etiket: "aday" }) +
      " güncel değer değildir.</p>";
    html += tablo(
      ["H", "F", "B", "K", "D"].map(function (k) {
        return hucre(k, e.sfc[k], { ondalik: 3, birim: "trilyon TL", kaynak: md, etiket: "aday" });
      }).join("") +
      hucre("Σ", e.sfc.sigma, { ondalik: 1, birim: "trilyon TL", kaynak: md, etiket: "aday" }) +
      hucre("F.4 2036 baz", e.f4_baz, { ondalik: 1, birim: "milyar TL", kaynak: md, etiket: "kanıt" }) +
      hucre("F.4 yüzde 10 varsayım", e.f4_bant[0], { ondalik: 1, birim: "milyar TL", kaynak: md, etiket: "aday" }) +
      hucre("F.4 yüzde 20 varsayım", e.f4_bant[1], { ondalik: 1, birim: "milyar TL", kaynak: md, etiket: "aday" }) +
      hucre("transfer", e.transfer_mn_usd, { ondalik: 0, birim: "mn USD", kaynak: md, etiket: "aday" }) +
      hucre("dönem kuru", e.kur, { ondalik: 2, kaynak: md, etiket: "aday" }) +
      hucre("transfer", e.transfer_tr_tl, { ondalik: 3, birim: "trilyon TL", kaynak: md, etiket: "aday" })
    );
    html += "<p>Kapanış belgede " + (e.kapanis_ok ? "kapanış_ok" : "kapalı değil") +
      ". F→D transferi belgenin yazdığı çarpımdır: " +
      rakam(e.transfer_mn_usd, { ondalik: 0, birim: "mn USD", kaynak: md, etiket: "aday" }) +
      " × " + rakam(e.kur, { ondalik: 2, kaynak: md, etiket: "aday" }) +
      " = " + rakam(e.transfer_tr_tl, { ondalik: 3, birim: "trilyon TL", kaynak: md, etiket: "aday" }) + ".</p>";
    const bol = document.getElementById("rant");
    bol.querySelectorAll(":scope > :not(h2)").forEach(function (n) { n.remove(); });
    bol.insertAdjacentHTML("beforeend", html);
  }

  function yanlisYaz() {
    const t = veri.m2.tl_para_stoku;
    const json = "para_arzi/m2_etki.json";
    const md = "para_arzi/REEL_RAHATLAMA.md";
    let html = "<article><h3>16.472,8 = M2</h3><p>Eşitlik düştü. TL para stoku " +
      rakam(t.tl_para_stoku, { ondalik: 1, birim: "milyar TL", kaynak: "ADIM45_BIRIM.md", etiket: "kanıt" }) +
      ", aynı çeyreğin M2'si " + rakam(t.m2, { ondalik: 4, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) +
      ", fark " + rakam(t.fark, { ondalik: 4, birim: "milyar TL", kaynak: json, etiket: "kanıt" }) + ".</p></article>";
    html += "<article><h3>Net reel rahatlama iddiası</h3><blockquote>" + esc(veri.reel.cumle) +
      "</blockquote><p>Hüküm " + esc(HUKUM[veri.reel.hukum.hukum] || veri.reel.hukum.hukum) + ". Tanım içi β = 0,5 hücresi " +
      rakam(veri.reel.hukum.n_beta05, { ondalik: 0, kaynak: "para_arzi/reel_rahatlama.json", etiket: "aday" }) +
      ", β = 1 hücresi " +
      rakam(veri.reel.hukum.n_beta1, { ondalik: 0, kaynak: "para_arzi/reel_rahatlama.json", etiket: "aday" }) +
      ". Kaynak <a href=\"../" + md + "\">REEL_RAHATLAMA.md</a>.</p></article>";
    html += "<article><h3>Stok yüzde 20 silindi</h3><p>«Yüzde 20» kaldırıldı. Yerine adım 1 tavan bandı yazıldı. Kaynak <a href=\"../BES_ADIM.md\">BES_ADIM.md</a>.</p></article>";
    const bol = document.getElementById("yanlis");
    bol.querySelectorAll(":scope > :not(h2)").forEach(function (n) { n.remove(); });
    bol.insertAdjacentHTML("beforeend", '<div class="kartlar">' + html + "</div>");
  }

  function jsonFark(c) {
    if (!c.kilitli) return null;
    const s = veri.m2.senaryo.find(function (x) { return x.ad === c.govde.ad; });
    const e = veri.enf.senaryo.find(function (x) { return x.ad === c.govde.ad; });
    let max = 0;
    ["adim4_tepe", "adim4_kalici", "baslik_stok", "baslik_yuzde", "tepe_stok"].forEach(function (k) {
      max = Math.max(max, Math.abs(c.m2[k] - s[k]));
    });
    ZT.YILLAR.forEach(function (yil) {
      max = Math.max(max,
        Math.abs(c.enf.yil[yil].toplam[0] - e.yil[yil].toplam[0]),
        Math.abs(c.enf.yil[yil].toplam[1] - e.yil[yil].toplam[1]));
    });
    return max;
  }

  function ciz() {
    const secim = oku();
    const durum = document.getElementById("durum");
    if (!Number.isFinite(secim.theta) || !Number.isFinite(secim.chi) || secim.theta < 0 || secim.theta > 1 || secim.chi < 0 || secim.chi > 1) {
      durum.textContent = "θ ve χ 0 ile 1 arasında olmalı.";
      return;
    }
    let c;
    try {
      c = ZT.hesapla(secim, { m2: veri.m2, enf: veri.enf, reel: veri.reel });
    } catch (err) {
      durum.textContent = err.message;
      return;
    }
    const fark = jsonFark(c);
    const govde = AD[c.govde.ad];
    if (c.kilitli && fark < 1e-6) {
      durum.textContent = "Gövde " + govde + ", θ ve χ kilitli. M2 ve enflasyon bandı JSON ile 10⁻⁶ altında.";
    } else if (c.kilitli) {
      durum.textContent = "Gövde " + govde + ", θ ve χ kilitli. JSON farkı " + fark + ".";
    } else {
      durum.textContent = "Gövde " + govde + " (κ, adres, I₀). θ veya χ kilitten farklı; formül aynı, bu satır JSON hücresi değildir.";
    }
    m2Yaz(c);
    enflasyonYaz(c);
    reelYaz(c);
  }

  document.querySelectorAll("#secici button[data-ad]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#secici button[data-ad]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      const s = veri.m2.senaryo.find(function (x) { return x.ad === b.getAttribute("data-ad"); });
      document.getElementById("theta").value = String(s.theta);
      document.getElementById("chi").value = String(s.chi);
      ciz();
    });
  });
  document.querySelectorAll("#secici button[data-beta]").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#secici button[data-beta]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      ciz();
    });
  });
  document.getElementById("theta").addEventListener("input", ciz);
  document.getElementById("chi").addEventListener("input", ciz);

  adimlariYaz();
  rantYaz();
  yanlisYaz();
  ciz();
})();
