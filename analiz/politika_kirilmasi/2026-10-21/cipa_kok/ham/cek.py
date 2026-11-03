import json,urllib.request,sys
def f(ser,start="01-01-2010",agg="avg"):
    s="-".join(ser)
    body={"type":"json","series":s,"aggregationTypes":"-".join([agg]*len(ser)),"formulas":"-".join(["0"]*len(ser)),
      "startDate":start,"endDate":"01-12-2019","frequency":"5","decimalSeperator":".","decimal":"4","dateFormat":"0","lang":"TR",
      "yon":"0","sira":"0","ozelFormuller":[],"groupSeperator":False,"isRaporSayfasi":False}
    r=urllib.request.Request("https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",data=json.dumps(body).encode(),headers={"Accept":"application/json","Content-Type":"application/json"},method="POST")
    return json.loads(urllib.request.urlopen(r,timeout=120).read().decode("utf-8-sig"))
for c in sys.argv[1:]:
    try:
        d=f([c]); it=[i for i in d["items"] if i.get(c.replace(".","_")) not in (None,"")]
        print(c,len(it),it[0]["Tarih"] if it else "",it[0].get(c.replace(".","_")) if it else "")
        json.dump(d,open(f"{c}.json","w"))
    except Exception as e: print(c,"HATA",e)
