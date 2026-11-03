import json,urllib.request,sys
FREQ="5"
def f(c,start="01-01-2014",end="01-10-2026"):
    body={"type":"json","series":c,"aggregationTypes":"avg","formulas":"0","startDate":start,"endDate":end,"frequency":FREQ,"decimalSeperator":".","decimal":"4","dateFormat":"0","lang":"TR","yon":"0","sira":"0","ozelFormuller":[],"groupSeperator":False,"isRaporSayfasi":False}
    r=urllib.request.Request("https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",data=json.dumps(body).encode(),headers={"Accept":"application/json","Content-Type":"application/json"},method="POST")
    return json.loads(urllib.request.urlopen(r,timeout=60).read().decode("utf-8-sig"))
for c in sys.argv[1:]:
    try:
        d=f(c);k=c.replace(".","_");it=[i for i in d["items"] if i.get(k) not in (None,"")]
        print(c,len(it),it[0]["Tarih"] if it else "",it[-1]["Tarih"] if it else "")
        if it: json.dump(d,open(c+".json","w"))
    except Exception as e: print(c,"HATA",str(e)[:80])
