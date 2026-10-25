import json,urllib.request,urllib.parse,time,csv
out=[]
for y in range(2015,2027):
    for m in range(1,13):
        if (y==2015 and m<12) or (y==2026 and m>9): continue
        b=urllib.parse.urlencode({'tabloNo':4,'yil':y,'ay':m,'paraBirimi':'TL','taraf':10001}).encode()
        try:
            r=json.loads(urllib.request.urlopen(urllib.request.Request('https://www.bddk.org.tr/BultenAylik/tr/Home/BasitRaporGetir',data=b),timeout=60).read())
            d=r['Json']['data'];d=json.loads(d) if isinstance(d,str) else d;cols=r['Json']['colNames']
            row={'ay':f'{y}-{m:02d}'}
            for x in d['rows']:
                c=x['cell']
                if c[1] in (1,5,9,12): row[f'r{c[1]}']=c[cols.index('Toplam')]
            out.append(row)
        except Exception as e: out.append({'ay':f'{y}-{m:02d}','hata':str(e)[:60]})
        time.sleep(0.5)
with open('bddk_tablo4.csv','w') as f:
    w=csv.DictWriter(f,['ay','r1','r5','r9','r12','hata']);w.writeheader();w.writerows(out)
