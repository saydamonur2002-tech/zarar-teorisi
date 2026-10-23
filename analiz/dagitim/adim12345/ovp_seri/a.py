import csv,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
# program -> (first column year, {metric: values}) ; kaynak OVP tabloları [VERİ]
P={
'2009-2011':(2009,{'prog':[2.3,2.0,1.7],'tufe':[7.5,6.5,5.5]}),
'2010-2012':(2009,{'prog':[-2.2,-0.8,-0.2,0.4],'fhh':[22.3,22.2,21.6,21.0],'vy_har':[17.7,19.4,19.4,19.3],'ozel':[0.5,1.0,0.8,0.7],'tufe':[5.9,5.3,4.9,4.8]}),
'2011-2013':(2010,{'prog':[-0.7,0.0,0.4,0.8],'fhh':[22.5,21.8,21.3,20.8],'vy_har':[19.7,19.7,19.6,19.5],'ozel':[0.4,1.1,0.9,0.7],'tufe':[7.5,5.3,5.0,4.9]}),
'2012-2014':(2011,{'prog':[0.9,1.0,1.2,1.4],'fhh':[21.1,21.1,20.9,20.4],'vy_har':[20.0,20.0,20.0,19.8],'ozel':[0.3,0.9,0.8,0.7],'tufe':[7.8,5.2,5,5]}),
'2013-2015':(2012,{'prog':[0.2,0.5,0.6,0.7],'fhh':[21.9,22.3,21.9,21.4],'vy_har':[20.0,20.8,20.5,20.2],'tufe':[7.4,5.3,5,5],'gd_tr':[17.6,18.3,17.6,17.2]}),
'2014-2016':(2012,{'fdd':[1.3,2.0,1.1,1.2,1.3],'vergi':[19.7,20.9,20.3,20.0,19.7],'fhh':[22.1,22.8,22.4,21.8,21.3],'vy_har':[20.2,21.4,20.9,20.8,20.6],'tufe':[6.2,6.8,5.3,5,5],'ozel':[0.5,0.6,0.6,0.4,0.2]}),
'2015-2017':(2013,{'fdd':[2.0,1.5,1.7,1.8,2.0],'vergi':[20.8,19.9,20.0,19.9,19.8],'fhh':[22.9,22.6,21.5,21.1,20.5],'vy_har':[21.5,20.5,20.7,20.7,20.6],'tufe':[7.4,9.4,6.3,5,5],'gd_tr':[15.2,15.0,14.7,14.4,14.3]}),
'2016-2018':(2014,{'fdd':[1.5,1.5,1.2,1.4,1.4],'vergi':[20.2,20.8,20.8,20.5,20.5],'fhh':[22.8,23.1,23.3,22.5,21.9],'vy_har':[20.8,21.4,21.4,21.2,21.1],'tufe':[8.2,8.8,7.5,6,5],'gd_tr':[18.3,18.5,19.4,18.7,18.2]}),
'2017-2019':(2015,{'fdd':[1.5,0.8,0.4,0.7,1.1],'vergi':[20.9,20.9,21.3,21.1,20.9],'fhh':[23.2,24.7,24.4,23.6,22.7],'vy_har':[21.5,21.5,21.9,21.8,21.6],'tufe':[8.8,7.5,6.5,5,5],'gd_tr':[18.6,19.7,19.6,19.1,18.7]}),
'2018-2020':(2016,{'kkgd_fh':[1.0,-0.3,0.1,0.4,1.0],'ozel':[None,0.4,0.2,0.3,0.2]}),
'2019-2021':(2017,{'fdd':[0.3,0.1,0.8,1.0,1.3],'vergi':[17.3,16.9,17.0,17.2,17.5],'fhh':[20.0,19.9,19.0,18.7,18.5]}),
'2020-2022':(2018,{'fdd':[0.0,-0.5,0.0,0.0,0.3],'vergi':[16.7,15.6,16.1,15.9,15.9],'fhh':[20.3,20.8,19.6,18.9,18.4]}),
'2021-2023':(2019,{'fdd':[-0.6,-2.1,-1.2,-0.7,-0.4],'vergi':[15.6,16.3,16.3,16.2,16.0],'fhh':[20.8,22.2,20.7,19.8,19.3]}),
'2022-2024':(2020,{'fdd':[-0.8,-0.8,-0.5,0.0,0.3],'vergi':[16.5,15.9,16.0,16.0,16.0],'fhh':[21.2,20.0,19.2,18.6,18.0],'vy_har':[16.9,16.3,16.3,16.4,16.4],'tufe':[14.6,16.2,9.8,8.0,7.6],'gd_tr':[14.8,13.7,13.3,13.0,12.5]}),
'2023-2025':(2021,{'fdd':[-0.3,-1.0,-0.5,0.5,1.3],'vergi':[16.1,16.9,17.2,17.2,17.2],'fhh':[19.6,20.9,20.9,19.9,19.1],'vy_har':[16.4,17.2,17.5,17.5,17.5],'tufe':[36.1,65.0,24.9,13.8,9.9],'gd_tr':[13.9,13.8,14.8,13.9,13.1]}),
'2024-2026':(2022,{'fdd':[1.1,-3.9,-3.4,0.0,0.7],'vergi':[15.7,16.8,18.0,18.0,18.0],'fhh':[17.5,23.2,23.9,20.6,19.9],'vy_har':[16.0,17.0,18.2,18.2,18.3],'tufe':[64.3,65.0,33.0,15.2,8.5],'gd_tr':[11.5,16.5,16.7,13.8,13.3]}),
'2025-2027':(2023,{'fdd':[-2.7,-1.9,0.0,0.3,0.6],'vergi':[17.0,17.2,18.1,18.1,18.1],'fhh':[22.3,22.4,20.8,20.6,20.4],'vy_har':[17.2,17.4,18.3,18.3,18.3],'tufe':[64.8,41.5,17.5,9.7,7.0],'gd_tr':[15.9,15.1,13.9,13.7,13.6]}),
'2026-2028':(2024,{'fdd':[-1.9,-0.3,0.0,0.3,0.5],'fhh':[21.3,20.3,21.0,20.6,20.5],'gd_tr':[14.8,13.4,14.6,14.1,13.8]}),
'2027-2029':(2025,{'fdd':[0.4,0.2,0.1,0.4,0.6],'vergi':[17.5,17.1,17.9,18.0,18.1],'fhh':[19.9,19.7,21.0,20.6,20.4],'vy_har':[17.7,17.4,18.2,18.3,18.4],'tufe':[30.9,28.4,21,13.5,9.0],'gd_tr':[13.4,13.1,13.4,12.9,12.6]}),
}
rows=[]
for p,(y0,m) in P.items():
  Y=int(p[:4])
  for k,v in m.items():
    for i,x in enumerate(v):
      if x is None: continue
      yr=y0+i; rol='gerceklesme' if yr<=Y-2 else ('GT' if yr==Y-1 else f't+{yr-Y+1}')
      rows.append(dict(program=p,metrik=k,yil=yr,rol=rol,deger=x,etiket='[VERİ]'))
with open('ovp_seri.csv','w',newline='') as f:
  w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
g=lambda p,k,y:next((r['deger'] for r in rows if r['program']==p and r['metrik']==k and r['yil']==y),None)
progs=list(P)
# gerçekleşme: sonraki OVP'nin 'gerceklesme' kolonu
act={}
for r in rows:
  if r['rol']=='gerceklesme': act[(r['metrik'],r['yil'])]=r['deger']
# hedef t+1 vs gerçekleşme; erteleme
out=[]
for i,p in enumerate(progs):
  Y=int(p[:4])
  for k in ['fdd','prog','vergi','fhh','tufe']:
    h=g(p,k,Y)
    if h is None: continue
    a=act.get((k,Y)); prev=g(progs[i-1],k,Y) if i>0 else None
    out.append(dict(program=p,metrik=k,hedef_yili=Y,hedef=h,gerceklesme=a,sapma=None if a is None else round(a-h,1),
      onceki_program_hedefi=prev,revizyon=None if prev is None else round(h-prev,1),
      uc_yil_hedef=g(p,k,Y+2),gt=g(p,k,Y-1)))
with open('hedef_gerceklesme.csv','w',newline='') as f:
  w=csv.DictWriter(f,out[0].keys());w.writeheader();w.writerows(out)
# uyum kaynağı: GT -> t+3
uy=[]
for p in progs:
  Y=int(p[:4]);gv,gV=g(p,'vergi',Y-1) or g(p,'vy_har',Y-1),g(p,'vergi',Y+2) or g(p,'vy_har',Y+2)
  vk='vergi' if g(p,'vergi',Y-1) is not None else 'vy_har'
  h0,h3=g(p,'fhh',Y-1),g(p,'fhh',Y+2)
  if None in (gv,gV,h0,h3): continue
  dv=round(gV-gv,1);dh=round(h0-h3,1)
  uy.append(dict(program=p,vergi_tanimi=vk,d_vergi=dv,harcama_kisma=dh,baskin='harcama' if dh>dv else 'vergi',etiket='[HESAP]'))
with open('uyum_kaynagi.csv','w',newline='') as f:
  w=csv.DictWriter(f,uy[0].keys());w.writeheader();w.writerows(uy)
# dolaylı payı (WB/IMF GFS, % gelir) -> pay [HESAP]
wb={l.split()[0]:{a.split(':')[0]:float(a.split(':')[1]) for a in l.split()[1:]} for l in open('wb_vergi.txt')}
dl=[]
for y in sorted(wb['GC.TAX.GSRV.RV.ZS']):
  d=wb['GC.TAX.GSRV.RV.ZS'][y]+wb['GC.TAX.INTT.RV.ZS'][y];i=wb['GC.TAX.YPKG.RV.ZS'][y];s=d/(d+i)
  dl.append(dict(yil=int(y),dolayli_payi=round(s*100,1),hane_payi_min=round((s*.7+(1-s)*.4)*100,1),hane_payi_max=round((s*1+(1-s)*.7)*100,1),
    vergi_gsyh_wb=wb['GC.TAX.TOTL.GD.ZS'].get(y),sub_transfer_harcama_payi=wb['GC.XPN.TRFT.ZS'].get(y),etiket='pay[HESAP] girdi[VERİ WB/IMF GFS] hane[VARSAYIM ovp_hane]'))
with open('dolayli_hane.csv','w',newline='') as f:
  w=csv.DictWriter(f,dl[0].keys());w.writeheader();w.writerows(dl)
# ücret/aylık reel
cpi={int(l.split()[0]):float(l.split()[1]) for l in open('cpi_wb.txt') if l.strip()}
au={2008:503.26,2009:546.48,2010:599.12,2011:658.95,2012:739.79,2013:803.68,2014:891.03,2015:1000.54,2016:1300.99,2017:1404.06,2018:1603.12,2019:2020.90,2020:2324.71,2021:2825.90,2022:5500.35,2023:11402.32,2024:17002.12,2025:22104.67,2026:28075.50}
em={2019:1000,2020:1500,2021:1500,2022:3500,2023:7500,2024:12500,2025:16881,2026:23552}
ww=[]
for y in range(2008,2027):
  c=cpi.get(y);r=lambda x:None if (x is None or c is None) else round(x*cpi[2025]/c)
  ww.append(dict(yil=y,asgari_net_yilsonu=au[y],asgari_reel_2025TL=r(au[y]),emekli_taban_yilsonu=em.get(y),emekli_reel_2025TL=r(em.get(y)),
   etiket='asgari 2008-21,2026[VERİ ÇSGB]; 2022-25[DOĞRULANMADI]; emekli[İKİNCİL derleme, RG atıflı]; reel[HESAP WB TÜFE yıllık ort.]'))
with open('ucret_emekli.csv','w',newline='') as f:
  w=csv.DictWriter(f,ww[0].keys());w.writeheader();w.writerows(ww)
fig,ax=plt.subplots(2,2,figsize=(14,10))
for p in progs:
  Y=int(p[:4]);k='fdd' if g(p,'fdd',Y) is not None else ('prog' if g(p,'prog',Y) is not None else None)
  if not k: continue
  ys=[y for y in range(Y-1,Y+3) if g(p,k,y) is not None];ax[0,0].plot(ys,[g(p,k,y) for y in ys],marker='.',ls='-' if k=='fdd' else ':',alpha=.8)
A=sorted((y,v) for (k,y),v in act.items() if k=='fdd');ax[0,0].plot(*zip(*A),'k-',lw=3,label='gerçekleşme (sonraki OVP)')
ax[0,0].set_title('MYB faiz dışı denge hedefleri (her çizgi bir OVP; nokta-çizgi=program tanımlı) %GSYH');ax[0,0].legend();ax[0,0].axhline(0,c='grey')
ax[0,1].bar([u['program'][:4] for u in uy],[u['d_vergi'] for u in uy],width=.4,label='Δvergi (GT→t+3)');ax[0,1].bar([str(int(u['program'][:4]))+' ' for u in uy],[u['harcama_kisma'] for u in uy],width=.4,label='faiz hariç harcama kısma')
ax[0,1].tick_params(axis='x',rotation=90);ax[0,1].legend();ax[0,1].set_title('Planlanan uyum kaynağı (puan GSYH) [HESAP]')
ax[1,0].plot([d['yil'] for d in dl],[d['dolayli_payi'] for d in dl],'b-o',label='dolaylı pay (WB/IMF)');ax[1,0].fill_between([d['yil'] for d in dl],[d['hane_payi_min'] for d in dl],[d['hane_payi_max'] for d in dl],alpha=.3,label='hane payı aralığı [VARSAYIM]');ax[1,0].legend();ax[1,0].set_title('Vergi içinde dolaylı pay ve hane payı aralığı %')
ax[1,1].plot([w['yil'] for w in ww],[w['asgari_reel_2025TL'] for w in ww],'g-o',label='asgari ücret net, 2025 TL');ax[1,1].plot([w['yil'] for w in ww],[w['emekli_reel_2025TL'] for w in ww],'r-o',label='en düşük emekli aylığı, 2025 TL');ax[1,1].legend();ax[1,1].set_title('Reel seyir (2026 TÜFE yok: çizilmedi)')
plt.tight_layout();plt.savefig('ovp_seri.png',dpi=110)
for f_ in ['hedef_gerceklesme.csv','uyum_kaynagi.csv','dolayli_hane.csv','ucret_emekli.csv']: print(open(f_).read())
