import csv,numpy as np
iso={'TUR':'TR','ARG':'AR','BRA':'BR','EGY':'EG','ZAF':'ZA','IDN':'ID','MEX':'MX','CHL':'CL','COL':'CO','HUN':'HU'}
W={}
for r in csv.DictReader(open('../drive/wdi_wid_birlesik_panel_dolu.csv')):
  W[(r['country'],int(r['year']))]=r
rows=list(csv.DictReader(open('epizod.csv')))
def d(c,t,k,q):
  f=lambda ys:[float(W[(c,y)][k])*100 for y in ys if (c,y) in W and W[(c,y)][k] and float(W[(c,y)]['wid_kalite_min'] or 0)>q]
  a,b=f(range(t-3,t)),f(range(t+1,t+4));return round(np.mean(b)-np.mean(a),2) if a and b else None
F=lambda x:None if x in('',None) else float(x)
out=[]
for q in (0,1):
  for r in rows:
    c=iso[r['ulke']];t=int(r['t0'])
    r[f'd_top10_wid_q{q}']=d(c,t,'ust10_gelir_payi',q);r[f'd_emek_q{q}']=d(c,t,'emek_payi',q)
    dl=F(r['d_dolayli'])
    r[f'Y2_q{q}']=None if None in (r[f'd_top10_wid_q{q}'],r[f'd_emek_q{q}']) else round(-r[f'd_top10_wid_q{q}']+r[f'd_emek_q{q}']-(dl or 0),2)
  for S in ['enf_sonra','d_faiz_gelir','d_npl']:
    ok=[r for r in rows if None not in (F(r[S]),r[f'Y2_q{q}'],F(r['kur_kaybi']),F(r['reel_faiz_sonra']))]
    n=len(ok)
    if n<5: out.append(dict(kosu=f'q>{q}',sonuc=S,n=n,not_='yetersiz'));continue
    y=np.log1p(np.array([F(r[S]) for r in ok])) if S=='enf_sonra' else np.array([F(r[S]) for r in ok])
    X0=np.c_[np.ones(n),[F(r['kur_kaybi']) for r in ok],[F(r['reel_faiz_sonra']) for r in ok]];Ys=np.array([r[f'Y2_q{q}'] for r in ok])
    def fit(X):
      b=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@b;return 1-e@e/((y-y.mean())@(y-y.mean())),e
    R0,e0=fit(X0);R1,_=fit(np.c_[X0,Ys]);ey=Ys-X0@np.linalg.lstsq(X0,Ys,rcond=None)[0]
    out.append(dict(kosu=f'q>{q}',sonuc=S,n=n,R2_R1R2=round(R0,2),R2_artis_H=round(R1-R0,2),kismi_r=round(np.corrcoef(e0,ey)[0,1],2),not_='H yönü r<0; enf log1p'))
w=csv.DictWriter(open('epizod_v2.csv','w',newline=''),rows[0].keys());w.writeheader();w.writerows(rows)
w=csv.DictWriter(open('testler_v2.csv','w',newline=''),['kosu','sonuc','n','R2_R1R2','R2_artis_H','kismi_r','not_']);w.writeheader();w.writerows(out)
for r in rows: print(r['ulke'],r['t0'],r['kur_kaybi'],r['enf_sonra'],r['d_top10_wid_q0'],r['d_emek_q0'],r['Y2_q0'],r['Y2_q1'])
for o in out: print(o)
