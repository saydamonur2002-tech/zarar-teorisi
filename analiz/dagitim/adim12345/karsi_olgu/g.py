import json,urllib.request,csv
C='TUR;ARG;BRA;EGY;ZAF;IDN;MEX;CHL;COL;HUN'
I=['SI.DST.10TH.10','GC.TAX.GSRV.RV.ZS','GC.TAX.YPKG.RV.ZS','GC.XPN.INTP.RV.ZS','FP.CPI.TOTL.ZG','FR.INR.RINR','FB.AST.NPER.ZS','PA.NUS.FCRF','NY.GDP.PCAP.KD','SL.GDP.PCAP.EM.KD']
out=[]
for i in I:
  u=f'https://api.worldbank.org/v2/country/{C}/indicator/{i}?format=json&date=2004:2025&per_page=2000'
  d=json.load(urllib.request.urlopen(u,timeout=90))[1] or []
  out+= [dict(ulke=x['countryiso3code'],gosterge=i,yil=int(x['date']),deger=x['value']) for x in d if x['value'] is not None]
w=csv.DictWriter(open('wb_ham.csv','w',newline=''),out[0].keys());w.writeheader();w.writerows(out);print(len(out))
