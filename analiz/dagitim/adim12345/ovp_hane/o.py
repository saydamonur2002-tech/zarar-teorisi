import csv,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
Y=['2025','2026GT','2027P','2028P','2029P']
G=[63241,85346,111207,133184,153141]  # VERİ OVP
vergi=[17.5,17.1,17.9,18.0,18.1]; fdh=[19.9,19.7,21.0,20.6,20.4]; fdd=[0.4,0.2,0.1,0.4,0.6]; prog=[-0.2,-0.3,-0.5,-0.2,0.1]; ct=[8.6,8.3,9.2,9.2,8.9]; gd_tr=[13.4,13.1,13.4,12.9,12.6]; vy=[24.3,24.3,24.8,24.9,25.1]
R=[]
for i,y in enumerate(Y): R+= [(y,'GSYH mlr TL',G[i],'VERİ OVP'),(y,'vergi/GSYH',vergi[i],'VERİ OVP T1.6'),(y,'faiz hariç harcama/GSYH',fdh[i],'VERİ'),(y,'FDD/GSYH',fdd[i],'VERİ'),(y,'program tanımlı denge/GSYH',prog[i],'VERİ'),(y,'cari transfer/GSYH',ct[i],'VERİ'),(y,'genel devlet transfer/GSYH',gd_tr[i],'VERİ T1.5'),(y,'vergi yükü SGK dahil',vy[i],'VERİ T1.4')]
# uyum 2026->2029
d_v=vergi[4]-vergi[1]; d_h=fdh[4]-fdh[1]; d_p=prog[4]-prog[1]
# dolaylı/dolaysız: doğrudan pay 2025 37.6, 2029 40.1 [İKİNCİL Yılmaz sunumu]
dol25=vergi[0]*(1-.376); dol29=vergi[4]*(1-.401); dir25=vergi[0]*.376; dir29=vergi[4]*.401
# sübvansiyon/destek 2027 [İKİNCİL bütçe sunumu]
en27=605; en26=605/1.62
S=[('enerji (elektrik+doğalgaz)',en26,en27),('sosyal yardım toplam',None,1341),('tarımsal destek programları',None,235),('tarımsal kredi sübvansiyonu',None,325),('sosyal konut finansmanı',None,250),('evde bakım',None,109),('65 yaş/engelli aylıkları',None,132),('doğum yardımı',None,84),('SGK işveren prim desteği',None,351),('asgari ücret GV istisnası (vergi harcaması)',None,1460)]
for k,a,b in S: R.append(('2027P',k+' mlr TL',b,'İKİNCİL (Yılmaz bütçe sunumu)')); R.append(('2027P',k+' /GSYH %',round(b/G[2]*100,2),'HESAP'))
R.append(('2026GT','enerji sübvansiyonu mlr TL (605/1,62)',round(en26),'HESAP (İKİNCİL girdi)')); R.append(('2026GT','enerji /GSYH %',round(en26/G[1]*100,2),'HESAP'))
R.append(('2026','KİT enerji görevlendirme Oca-Tem mlr TL',196.0,'İKİNCİL (BoldMedya; HMB)'))
R.append(('2026-07','en düşük emekli aylığı TL',23552,'İKİNCİL (TBMM önergesi, SGK atfı)'))
R.append(('2026-07','net asgari ücret TL',28075.5,'İKİNCİL (SBB haftalık atfı)'))
R.append(('2027','OVP TÜFE yıl sonu %',21.0,'VERİ OVP'))
csv.writer(open('ovp_hane.csv','w')).writerows([['yil','kalem','deger','etiket']]+R)
# hane payı (2026GT->2029P vergi artışı)
H=[]
for gv in (0.4,0.7):  # dolaysız artışın hane (GV) payı VARSAYIM
  for yan in (0.7,1.0):
    dd=dol29-dol25; dr=dir29-dir25
    H.append((gv,yan,round(dd*yan+dr*gv,2),round(dr*(1-gv)+dd*(1-yan),2)))
csv.writer(open('hane_payi.csv','w')).writerows([['dolaysiz_hane_payi_VARSAYIM','dolayli_yansima_VARSAYIM','hane_puan_HESAP','firma_puan_HESAP']]+H)
print('d_vergi',round(d_v,1),'d_harcama',round(d_h,1),'d_prog',round(d_p,1),'dolaylı',round(dol25,2),round(dol29,2),'dolaysız',round(dir25,2),round(dir29,2)); print(H); print('enerji26',en26,en26/G[1]*100,en27/G[2]*100)
f,a=plt.subplots(1,3,figsize=(16,4.5))
a[0].plot(Y,vergi,'o-',label='vergi');a[0].plot(Y,fdh,'s-',label='faiz hariç harcama');a[0].set_title('OVP 2027–29, %GSYH [VERİ]');a[0].legend()
a[1].bar(Y,fdd,label='FDD');a[1].plot(Y,prog,'ro-',label='program tanımlı');a[1].axhline(0,c='k');a[1].set_title('Denge %GSYH [VERİ]');a[1].legend()
a[2].bar(['dolaylı 2025','dolaylı 2029','dolaysız 2025','dolaysız 2029'],[dol25,dol29,dir25,dir29],color=['#c66','#c66','#69c','#69c']);a[2].set_title('Vergi/GSYH bileşimi [HESAP; pay İKİNCİL]')
plt.tight_layout();plt.savefig('ovp_hane.png',dpi=110)
