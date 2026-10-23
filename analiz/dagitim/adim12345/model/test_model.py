from model import run,MER
def test():
    c=run(**MER)
    assert round(c['net_faiz'],1)==738.2 and round(c['oran_A1_G'],1)==64.3 and round(c['oran_A1_K'],1)==55.3 and round(c['oran_A1_B'],1)==69.9
    assert round(c['ticari_borc'])==14602 and round(c['serbest_nakit'],1)==208.4 and c['oran_A2_G']==c['oran_A1_G']
if __name__=='__main__':test();print('TEST OK')
