"use strict";

/**
 * Beş adımın M2, enflasyon köprüsü ve net reel rahatlama formülleri.
 * para_arzi/m2_etki.py, enflasyon_etki.py ve reel_rahatlama.py ile aynı aritmetik.
 * Katsayılar çağıranın verdiği JSON belgelerinden okunur; burada sayı uydurulmaz.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.ZT = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const KREDI_PAY = 0.08;
  const GERCEK_YP = 6639.4;
  const I0 = 53.1925;
  const PI0 = 29.73;
  const KIRA_W = 0.068028;
  const KIRA_ALT = [4783.0, 30291.0];
  const KIRA_UST = [10291.0, 24783.0];
  const KAPPA = { dusuk: 0.25, orta: 0.5, yuksek: 1.0 };
  const YILLAR = ["2027", "2028", "2029", "2030", "2031"];
  const BETALAR = [0, 0.5, 1];

  function pyRound(x, n) {
    const p = 10 ** n;
    const y = x * p;
    const sign = y < 0 ? -1 : 1;
    const ay = Math.abs(y);
    const floor = Math.floor(ay + 1e-12);
    const frac = ay - floor;
    let k;
    if (Math.abs(frac - 0.5) <= 1e-8) k = floor % 2 === 0 ? floor : floor + 1;
    else k = frac > 0.5 ? floor + 1 : floor;
    return (sign * k) / p;
  }

  function adim4(theta, chi, adres) {
    const tepe = pyRound(theta * adres, 4);
    const kalici = pyRound(chi * tepe, 4);
    return {
      tepe: tepe,
      kalici: kalici,
      ikinci_tur_tepe: pyRound(KREDI_PAY * tepe, 4),
      ikinci_tur_kalici: pyRound(KREDI_PAY * kalici, 4),
    };
  }

  function m2Satir(adim12, a4, m2) {
    const baslik = adim12 + a4.kalici;
    const tepeStok = adim12 + a4.tepe;
    return {
      adim12_m2: adim12,
      adim3_m2: 0,
      adim45_m2: 0,
      adim5_m2: 0,
      adim4_tepe: a4.tepe,
      adim4_kalici: a4.kalici,
      ikinci_tur_tepe_yillik: a4.ikinci_tur_tepe,
      ikinci_tur_kalici_yillik: a4.ikinci_tur_kalici,
      baslik_stok: pyRound(baslik, 4),
      baslik_yuzde: pyRound((100 * baslik) / m2, 4),
      tepe_stok: pyRound(tepeStok, 4),
      tepe_yuzde: pyRound((100 * tepeStok) / m2, 4),
    };
  }

  function m1Cift(carpan, dm2, vadesiz) {
    const ust = Math.min(carpan * GERCEK_YP, vadesiz, dm2);
    return [0, Math.max(0, ust)];
  }

  function dlogSeviye(m1, m2, dm1, dm2) {
    if (dm2 < dm1 - 1e-6 || m1 <= dm1 || m2 <= dm2) {
      throw new Error("para şoku stoğu aşıyor");
    }
    const dlm1 = Math.log(m1 - dm1) - Math.log(m1);
    const dlr = Math.log((m2 - dm2) / (m1 - dm1)) - Math.log(m2 / m1);
    return [dlm1, dlr];
  }

  function dlogAradan(m1, m2, dm1a, dm2a, dm1b, dm2b) {
    const a1 = m1 - dm1a;
    const a2 = m2 - dm2a;
    const b1 = m1 - dm1b;
    const b2 = m2 - dm2b;
    if (Math.min(a1, a2, b1, b2) <= 0) throw new Error("ara düzey eksi");
    return [Math.log(b1) - Math.log(a1), Math.log(b2 / b1) - Math.log(a2 / a1)];
  }

  function paraNokta(b1, b2, dlm1, dlr) {
    return 100 * (b1 * dlm1 + b2 * dlr);
  }

  function tekPuan(noktaKat, dlog) {
    return 100 * noktaKat * dlog;
  }

  function kiraPuan(kapsam) {
    const lo = -100 * KIRA_W * kapsam * (KIRA_ALT[0] / KIRA_ALT[1]);
    const hi = -100 * KIRA_W * kapsam * (KIRA_UST[0] / KIRA_UST[1]);
    return lo <= hi ? [lo, hi] : [hi, lo];
  }

  function bant(paraAlt, paraUst, mali, kredi) {
    const vals = [];
    for (const p of [paraAlt, paraUst]) {
      for (const m of [0, mali]) vals.push(p + m + kredi);
    }
    return [Math.min.apply(null, vals), Math.max.apply(null, vals)];
  }

  function bosHucre() {
    return bant(0, 0, 0, 0);
  }

  function enflasyon(g) {
    const dm1Tepe = m1Cift(g.theta, g.tepe, g.vadesiz);
    const dm1Kal = m1Cift(g.chi * g.theta, g.kalici, g.vadesiz);
    const paraTepe = {};
    const paraGeri = {};
    for (const adim of ["alt", "ust"]) {
      const i = adim === "alt" ? 0 : 1;
      const dTepe = dlogSeviye(g.m1, g.m2, dm1Tepe[i], g.tepe);
      const dGeri = dlogAradan(g.m1, g.m2, dm1Tepe[i], g.tepe, dm1Kal[i], g.kalici);
      paraTepe[adim] = paraNokta(g.b1, g.b2, dTepe[0], dTepe[1]);
      paraGeri[adim] = paraNokta(g.b1, g.b2, dGeri[0], dGeri[1]);
    }
    const mali = -100 * g.I / g.gsyh;
    function krediDlog(ak) {
      if (ak > g.krediStok) throw new Error("kredi akışı stoktan büyük");
      return ak === 0 ? 0 : Math.log(1 - ak / g.krediStok);
    }
    const dlogTepe = krediDlog(g.akimTepe);
    const dlogKal = krediDlog(g.akimKalici);
    const kredi = {
      tepe: tekPuan(g.dNokta, dlogTepe),
      kalici: tekPuan(g.dNokta, dlogKal),
    };
    const buyume = {
      tepe: tekPuan(g.hNokta, dlogTepe),
      kalici: tekPuan(g.hNokta, dlogKal),
    };
    const h29 = bant(paraTepe.alt, paraTepe.ust, mali, 0);
    const h30 = bant(0, 0, mali, kredi.tepe);
    const h31 = bant(paraGeri.alt, paraGeri.ust, mali, kredi.kalici);
    const s29 = bant(paraTepe.alt, paraTepe.ust, mali, 0);
    const s30 = bant(0, 0, mali, 0);
    const s31 = bant(paraGeri.alt, paraGeri.ust, mali, 0);
    function hucre(toplam, kredisiz, paraAlt, paraUst, krediNokta, maliDeger) {
      return {
        toplam: toplam,
        toplam_kredisiz: kredisiz,
        para_alt: paraAlt,
        para_ust: paraUst,
        kredi: krediNokta,
        kur: 0,
        maliyet: [0, maliDeger],
        adim45: 0,
      };
    }
    const sifir = hucre(bosHucre(), bosHucre(), 0, 0, 0, 0);
    return {
      dm1_tepe: dm1Tepe,
      dm1_kalici: dm1Kal,
      para_tepe: paraTepe,
      para_geri: paraGeri,
      mali: mali,
      kredi: kredi,
      buyume: buyume,
      kira: kiraPuan(g.kapsam),
      hiz_tepe: -g.tepe / g.m2,
      hiz_kalici: -g.kalici / g.m2,
      yil: {
        2027: sifir,
        2028: sifir,
        2029: hucre(h29, s29, paraTepe.alt, paraTepe.ust, 0, mali),
        2030: hucre(h30, s30, 0, 0, kredi.tepe, mali),
        2031: hucre(h31, s31, paraGeri.alt, paraGeri.ust, kredi.kalici, mali),
      },
    };
  }

  function iBeta(beta, dpi) {
    return Math.max(0, I0 + beta * dpi);
  }

  function reelHucre(i0Milyar, beta, dpi) {
    const p = 1 + (PI0 + dpi) / 100;
    if (p <= 0) {
      return { durum: "tanimlanamadi", delta_pi: dpi, beta: beta };
    }
    const oran = iBeta(beta, dpi);
    const nominal = (i0Milyar * oran) / I0;
    const sabit = i0Milyar / (1 + PI0 / 100);
    const reel = nominal / p;
    return {
      durum: "olculdu",
      beta: beta,
      delta_pi: dpi,
      tanim_disi: Math.abs(dpi) > I0,
      hukme_girer: dpi < 0 && Math.abs(dpi) <= I0,
      i: oran,
      taban_bagli: I0 + beta * dpi < 0,
      nominal: nominal,
      fazlalik: i0Milyar - nominal,
      reel: reel,
      sabit_reel: sabit,
      net: reel - sabit,
      etiket: "aday",
    };
  }

  function hukum(hucreler) {
    const kapsam = hucreler.filter(function (h) {
      return h.hukme_girer && (h.beta === 0.5 || h.beta === 1) && h.durum === "olculdu";
    });
    const bir = kapsam.filter(function (h) { return h.beta === 1; });
    const yari = kapsam.filter(function (h) { return h.beta === 0.5; });
    const yanlis = yari.some(function (h) { return h.net < 0; });
    const ayakta = bir.length > 0 && bir.every(function (h) { return h.net > 0; });
    return {
      hukum: yanlis ? "yanlis" : ayakta ? "ayakta" : "ayakta_degil",
      n_beta1: bir.length,
      n_beta05: yari.length,
      beta1_hepsi_pozitif: ayakta,
      beta05_herhangi_negatif: yanlis,
    };
  }

  function govde(ad, belgeler) {
    const s = belgeler.m2.senaryo.find(function (x) { return x.ad === ad; });
    const e = belgeler.enf.senaryo.find(function (x) { return x.ad === ad; });
    if (!s || !e) throw new Error("senaryo yok");
    return {
      ad: ad,
      theta_kilit: s.theta,
      chi_kilit: s.chi,
      adres: s.adres,
      adim12: s.adim12_m2,
      I: e.maliyet.I,
      kapsam: e.kira.kapsama,
      kappa: KAPPA[ad],
    };
  }

  function hesapla(secim, belgeler) {
    const g0 = govde(secim.ad, belgeler);
    const theta = secim.theta;
    const chi = secim.chi;
    const enf = belgeler.enf;
    const a4 = adim4(theta, chi, g0.adres);
    const m2 = m2Satir(g0.adim12, a4, enf.m2);
    const blok = enflasyon({
      theta: theta,
      chi: chi,
      tepe: a4.tepe,
      kalici: a4.kalici,
      akimTepe: a4.ikinci_tur_tepe,
      akimKalici: a4.ikinci_tur_kalici,
      I: g0.I,
      kapsam: g0.kapsam,
      m1: enf.m1,
      m2: enf.m2,
      vadesiz: enf.vadesiz_yp,
      krediStok: enf.kredi_stok_milyar,
      gsyh: enf.gsyh_2025,
      b1: enf.para.b1.nokta,
      b2: enf.para.b2.nokta,
      dNokta: enf.kredi_model.d.nokta,
      hNokta: enf.kredi_model.h.nokta,
    });
    const reel = {};
    YILLAR.forEach(function (yil) {
      if (yil < "2029") return;
      reel[yil] = blok.yil[yil].toplam.map(function (dpi) {
        return BETALAR.map(function (beta) {
          return reelHucre(g0.I, beta, dpi);
        });
      });
    });
    return {
      govde: g0,
      theta: theta,
      chi: chi,
      beta: secim.beta,
      kilitli: Math.abs(theta - g0.theta_kilit) < 1e-12 && Math.abs(chi - g0.chi_kilit) < 1e-12,
      m2: m2,
      adim4: a4,
      enf: blok,
      reel: reel,
    };
  }

  return {
    KREDI_PAY: KREDI_PAY,
    GERCEK_YP: GERCEK_YP,
    I0: I0,
    PI0: PI0,
    KIRA_W: KIRA_W,
    KAPPA: KAPPA,
    YILLAR: YILLAR,
    BETALAR: BETALAR,
    pyRound: pyRound,
    adim4: adim4,
    hesapla: hesapla,
    reelHucre: reelHucre,
    hukum: hukum,
  };
});
