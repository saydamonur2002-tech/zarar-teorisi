import csv,numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
D={}
for r in csv.DictReader(open('wb_ham.csv')): D[(r['ulke'],r['gosterge'],int(r['yil']))]=float(r['deger'])
E=[('TUR',2018),('ARG',2018),('BRA',2015),('EGY',2016),('EGY',2022),('ZAF',2015),('IDN',2013),('IDN',2018),('MEX',2015),('CHL',2019),('COL',2015),('HUN',2008)]
def m(c,i,ys):
  v=[D[(c,i,y)] for y in ys if (c,i,y) in D];return np.mean(v) if v else None
def dif(c,i,t):
  a=m(c,i,range(t-3,t));b=m(c,i,range(t+1,t+4));return None if None in(a,b) else b-a
rows=[]
for c,t in E:
  fx=None
  if (c,'PA.NUS.FCRF',t-1) in D and (c,'PA.NUS.FCRF',t+1) in D: fx=(D[(c,'PA.NUS.FCRF',t+1)]/D[(c,'PA.NUS.FCRF',t-1)]-1)*100
  dl=lambda y:(D[(c,'GC.TAX.GSRV.RV.ZS',y)]/(D[(c,'GC.TAX.GSRV.RV.ZS',y)]+D[(c,'GC.TAX.YPKG.RV.ZS',y)])*100) if (c,'GC.TAX.GSRV.RV.ZS',y) in D and (c,'GC.TAX.YPKG.RV.ZS',y) in D else None
  pre=[dl(y) for y in range(t-3,t) if dl(y)];post=[dl(y) for y in range(t+1,t+4) if dl(y)]
  ddl=np.mean(post)-np.mean(pre) if pre and post else None
  g0=D.get((c,'NY.GDP.PCAP.KD',t-1));rec=None
  if g0:
    for y in range(t,2025):
      if D.get((c,'NY.GDP.PCAP.KD',y),0)>=g0: rec=y-t;break
  rows.append(dict(ulke=c,t0=t,kur_kaybi=fx,d_top10=dif(c,'SI.DST.10TH.10',t),d_dolayli=ddl,reel_faiz_sonra=m(c,'FR.INR.RINR',range(t,t+4)),
   enf_sonra=m(c,'FP.CPI.TOTL.ZG',range(t+1,t+4)),d_faiz_gelir=dif(c,'GC.XPN.INTP.RV.ZS',t),d_npl=dif(c,'FB.AST.NPER.ZS',t),toparlanma_yil=rec))
for r in rows:
  for k,v in r.items():
    if isinstance(v,float): r[k]=round(v,2)
  r['Y_skor']=None if None in (r['d_top10'],r['d_dolayli']) else round(-r['d_top10']-r['d_dolayli'],2)
  r['etiket']='girdi[VERİ WB/PIP/IMF GFS]; fark/skor[HESAP]; R3 ÖLÇÜLMEDİ'
w=csv.DictWriter(open('epizod.csv','w',newline=''),rows[0].keys());w.writeheader();w.writerows(rows)
for r in rows: print(r)
# test b: her sonuç için
res=[]
for S in ['enf_sonra','d_faiz_gelir','d_npl','toparlanma_yil']:
  ok=[r for r in rows if None not in (r[S],r['Y_skor'],r['kur_kaybi'],r['reel_faiz_sonra'])]
  n=len(ok)
  if n<5: res.append(dict(sonuc=S,n=n,not_='yetersiz'));continue
  y=np.array([r[S] for r in ok]);X0=np.c_[np.ones(n),[r['kur_kaybi'] for r in ok],[r['reel_faiz_sonra'] for r in ok]];Ys=np.array([r['Y_skor'] for r in ok])
  def r2(X):
    b=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@b;return 1-e@e/((y-y.mean())@(y-y.mean())),e
  R0,e0=r2(X0);R1,_=r2(np.c_[X0,Ys]);ey=Ys-X0@np.linalg.lstsq(X0,Ys,rcond=None)[0]
  pc=np.corrcoef(e0,ey)[0,1];sp=np.corrcoef(np.argsort(np.argsort(Ys)),np.argsort(np.argsort(y)))[0,1]
  res.append(dict(sonuc=S,n=n,R2_R1R2=round(R0,2),R2_artis_H=round(R1-R0,2),kismi_r=round(pc,2),spearman_ham=round(sp,2),not_='H yönü: r<0 (üste yük→daha iyi)'))
w=csv.DictWriter(open('testler.csv','w',newline=''),['sonuc','n','R2_R1R2','R2_artis_H','kismi_r','spearman_ham','not_']);w.writeheader();w.writerows(res)
for r in res: print(r)
ok=[r for r in rows if r['Y_skor'] is not None and r['enf_sonra'] is not None]
fig,ax=plt.subplots(1,2,figsize=(12,5))
for r in ok: ax[0].scatter(r['Y_skor'],r['enf_sonra']);ax[0].annotate(f"{r['ulke']}{r['t0']}",(r['Y_skor'],r['enf_sonra']))
ax[0].set_xlabel('Y skoru (+ = yük üste) [HESAP]');ax[0].set_ylabel('sonraki 3y ort. enflasyon %');ax[0].set_yscale('symlog')
ok2=[r for r in rows if r['kur_kaybi'] is not None and r['enf_sonra'] is not None]
for r in ok2: ax[1].scatter(r['kur_kaybi'],r['enf_sonra'],c='r' if (r['reel_faiz_sonra'] or 0)<0 else 'b');ax[1].annotate(f"{r['ulke']}{r['t0']}",(r['kur_kaybi'],r['enf_sonra']))
ax[1].set_xlabel('kur kaybı % (t-1→t+1)');ax[1].set_title('kırmızı: negatif reel faiz');ax[1].set_yscale('symlog')
plt.tight_layout();plt.savefig('karsi_olgu.png',dpi=110)
