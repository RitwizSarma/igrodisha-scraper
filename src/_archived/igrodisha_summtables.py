import requests, os, time
import pandas as pd

class progressbar():
    '''Default progress bar used for multiple functions.'''
    def dispBar(iter, constr,  res):
        pct = 100 * (iter/constr)
        blno = int((pct/100) * res)
        bl_str = "▒" * blno
        if iter != constr: line_str = "_" * (res-blno)
        else: line_str = ""
        print(bl_str+line_str, "%.3f percent done..." %pct, end='\r')

def appends(*args):
    global dists, regoffs, nvils, nplt 
    dists, regoffs, nvils, nplt = [], [], [], []
    dists.append(args[0])
    regoffs.append(args[1])
    nvils.append(args[2])
    nplt.append(args[3])

s = requests.session()
regoff_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetRegoffice"
vil_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetVillage"
plot_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetPlotDtl"
headers={
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, br',
    'Connection':'keep-alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'sec-ch-ua' : '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows'
    }

dist = list(range(1,31))

for d_id in dist:
    time.sleep(0.5)
    rctr = 0
    print("Starting district %i..." %d_id)
    regoff_payl = {"distId":d_id}
    try:
        regoff_resp = s.post(regoff_api,json=regoff_payl, headers=headers)
        regoff_json = regoff_resp.json()        
    except:
        print(regoff_resp.status_code)
        print(regoff_resp)
        break
    nreg = len(regoff_json['d'])
    for regoff in regoff_json['d']:
        time.sleep(0.25)
        pltcnt = 0
        rctr+=1
        regn = regoff['REGOFF_NAME']
        vil_payl = {'RegoffId':regoff['REGOFF_ID']}
        try:
            vctr=0
            vil_json = s.post(vil_api,json=vil_payl, headers=headers).json()
            nvill = len(vil_json['d'])
            for vil in vil_json['d']:
                time.sleep(0.5)
                vctr+=1
                plot_payl = {'StrVillageId':vil['VILL_ID']}  
                plot_json = s.post(plot_api, json=plot_payl, headers=headers).json()
                pltcnt = pltcnt + len(plot_json) 
                progressbar.dispBar(vctr, len(vil_json['d']), 50)
        except:
            print(regn)
            nvill = 0
        appends(str(d_id), regn, nvill, nplt)
        progressbar.dispBar(rctr, nreg, 50)
    
df = pd.DataFrame({'District':dists, 'RegistrationOff':regoffs, 'NumberOfVillages':nvils})
df.to_csv("C:/Codes/Try/OdishaSummTable3.csv")

