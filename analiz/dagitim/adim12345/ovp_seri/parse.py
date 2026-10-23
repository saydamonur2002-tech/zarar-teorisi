import re,glob,json,sys
num=r'-?\d{1,3}(?:\.\d{3})*,\d|-?\d+,\d'
def nums(s): return [float(x.replace('.','').replace(',','.')) for x in re.findall(num,s)]
L={'fdd':r'^\s*(Merkez[iî] Yönetim Bütçesi )?Faiz Dışı (Denge|Fazla)(sı)?\s', 'vergi':r'^\s*Genel Bütçe Vergi Gelirleri', 'fhh':r'^\s*(Faiz Hariç Harcamalar|Merkez[iî] Yönetim Bütçesi Faiz Dışı Harcamaları)', 'vy_har':r'Vergi Yükü \(Sosyal Güvenlik Primleri Hari', 'vy_dah':r'Vergi Yükü \(Sosyal Güvenlik Primleri Da|Dahil Vergi Yükü|Dâhil Vergi Yükü','tufe':r'TÜFE Yıl ?Sonu','ozel':r'Kamu (Kesimi )?Özelleştirme Geliri|^\s*Özelleştirme Gelirleri \(','gd_tr':r'^\s*Transfer Harcamaları','prog':r'Program Tanımlı (Denge|Faiz Dışı)'}
out={}
for f in sorted(glob.glob('pdf/20*.txt')):
  p=f[4:-4]; T=open(f,errors='ignore').read().split('\n'); r={}
  for k,pat in L.items():
    hits=[]
    for i,l in enumerate(T):
      if re.search(pat,l,re.I):
        v=nums(l)
        if len(v)>=4: hits.append(v[-5:] if len(v)>=5 else v)
    r[k]=hits
  out[p]=r
json.dump(out,open('raw.json','w'),ensure_ascii=False)
for p,r in out.items():
  print('==',p)
  for k,h in r.items(): print(' ',k,h[-3:])
