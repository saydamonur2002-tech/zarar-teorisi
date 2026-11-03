"use strict";

const fs = require("fs");
const path = require("path");
const z = require("./formuller.js");

const kok = path.resolve(__dirname, "..");
const m2 = JSON.parse(fs.readFileSync(path.join(kok, "para_arzi/m2_etki.json"), "utf8"));
const enf = JSON.parse(fs.readFileSync(path.join(kok, "para_arzi/enflasyon_etki.json"), "utf8"));
const reel = JSON.parse(fs.readFileSync(path.join(kok, "para_arzi/reel_rahatlama.json"), "utf8"));
const belgeler = { m2: m2, enf: enf, reel: reel };

let hata = 0;
function yakin(a, b, tol, ad) {
  if (typeof a !== "number" || typeof b !== "number" || Math.abs(a - b) > tol) {
    console.error("FARK", ad, a, b, typeof a === "number" && typeof b === "number" ? a - b : "");
    hata += 1;
  }
}

const M2_ALAN = [
  "adim4_tepe",
  "adim4_kalici",
  "ikinci_tur_tepe_yillik",
  "ikinci_tur_kalici_yillik",
  "baslik_stok",
  "baslik_yuzde",
  "tepe_stok",
  "tepe_yuzde",
  "adim12_m2",
  "adim3_m2",
  "adim45_m2",
  "adim5_m2",
];

for (const s of m2.senaryo) {
  const c = z.hesapla({ ad: s.ad, theta: s.theta, chi: s.chi, beta: 0.5 }, belgeler);
  if (!c.kilitli) {
    console.error("kilit degil", s.ad);
    hata += 1;
  }
  for (const alan of M2_ALAN) yakin(c.m2[alan], s[alan], 1e-6, s.ad + " m2 " + alan);
  const e = enf.senaryo.find(function (x) { return x.ad === s.ad; });
  yakin(c.enf.kira[0], e.kira.puan[0], 1e-6, s.ad + " kira0");
  yakin(c.enf.kira[1], e.kira.puan[1], 1e-6, s.ad + " kira1");
  yakin(c.enf.mali, e.maliyet.alfa1, 1e-6, s.ad + " mali");
  yakin(c.enf.dm1_tepe[0], e.dm1_tepe[0], 1e-6, s.ad + " dm1 tepe alt");
  yakin(c.enf.dm1_tepe[1], e.dm1_tepe[1], 1e-6, s.ad + " dm1 tepe ust");
  yakin(c.enf.dm1_kalici[0], e.dm1_kalici[0], 1e-6, s.ad + " dm1 kal alt");
  yakin(c.enf.dm1_kalici[1], e.dm1_kalici[1], 1e-6, s.ad + " dm1 kal ust");
  yakin(c.enf.kredi.tepe, e.kredi.tepe.nokta, 1e-6, s.ad + " kredi tepe");
  yakin(c.enf.kredi.kalici, e.kredi.kalici.nokta, 1e-6, s.ad + " kredi kalici");
  yakin(c.enf.buyume.tepe, e.buyume.tepe.nokta, 1e-6, s.ad + " buyume tepe");
  yakin(c.enf.buyume.kalici, e.buyume.kalici.nokta, 1e-6, s.ad + " buyume kalici");
  yakin(c.enf.para_tepe.alt, e.para_tepe.alt.nokta, 1e-6, s.ad + " para tepe alt");
  yakin(c.enf.para_tepe.ust, e.para_tepe.ust.nokta, 1e-6, s.ad + " para tepe ust");
  yakin(c.enf.para_geri.alt, e.para_geri.alt.nokta, 1e-6, s.ad + " para geri alt");
  yakin(c.enf.para_geri.ust, e.para_geri.ust.nokta, 1e-6, s.ad + " para geri ust");
  for (const yil of ["2027", "2028", "2029", "2030", "2031"]) {
    yakin(c.enf.yil[yil].toplam[0], e.yil[yil].toplam[0], 1e-6, s.ad + " " + yil + " toplam0");
    yakin(c.enf.yil[yil].toplam[1], e.yil[yil].toplam[1], 1e-6, s.ad + " " + yil + " toplam1");
    yakin(c.enf.yil[yil].toplam_kredisiz[0], e.yil[yil].toplam_kredisiz[0], 1e-6, s.ad + " " + yil + " kredisiz0");
    yakin(c.enf.yil[yil].toplam_kredisiz[1], e.yil[yil].toplam_kredisiz[1], 1e-6, s.ad + " " + yil + " kredisiz1");
    yakin(c.enf.yil[yil].kredi, e.yil[yil].kredi, 1e-6, s.ad + " " + yil + " kredi");
  }
}

for (const h of reel.satirlar) {
  const c = z.reelHucre(h.I0, h.beta, h.delta_pi);
  const ad = h.senaryo + " " + h.yil + " b" + h.beta + " dpi" + h.delta_pi;
  yakin(c.nominal, h.nominal, 1e-6, ad + " nominal");
  yakin(c.net, h.net, 1e-6, ad + " net");
  yakin(c.reel, h.reel, 1e-6, ad + " reel");
  yakin(c.i, h.i, 1e-6, ad + " i");
  yakin(c.fazlalik, h.fazlalik, 1e-6, ad + " fazlalik");
  if (c.tanim_disi !== h.tanim_disi || c.hukme_girer !== h.hukme_girer || c.taban_bagli !== h.taban_bagli) {
    console.error("BAYRAK", ad, c.tanim_disi, h.tanim_disi, c.hukme_girer, h.hukme_girer, c.taban_bagli, h.taban_bagli);
    hata += 1;
  }
}

const tum = reel.satirlar.map(function (h) { return z.reelHucre(h.I0, h.beta, h.delta_pi); });
const hk = z.hukum(tum);
if (hk.hukum !== reel.hukum.hukum) {
  console.error("HUKUM", hk, reel.hukum);
  hata += 1;
}

if (z.GERCEK_YP !== 6639.4 || z.KREDI_PAY !== 0.08 || z.I0 !== 53.1925 || z.PI0 !== 29.73) {
  console.error("SABIT");
  hata += 1;
}

if (hata) {
  console.error("hata sayisi", hata);
  process.exit(1);
}
console.log("esit", m2.senaryo.length, "senaryo,", reel.satirlar.length, "reel hucre, hukum", hk.hukum);
