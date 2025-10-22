'''CLEAN SCRIPT FOR 3P USER, PL ADD FILELOC AT LN10 BEFORE RUNNING'''
# add timecheck for resumefxn
# consider recheck resumefxn

import os
import argparse
import pandas as pd
import requests, time
from helpers_enduser import *

# base_dir = YOUR FOLDER NAME HERE
# Make base_dir configurable via CLI or env var. Default to a POSIX-friendly ./data
DEFAULT_BASE_DIR = os.environ.get('IGRO_BASE_DIR', os.path.join('.', 'data'))

def parse_args():
    p = argparse.ArgumentParser(description='igrodisha scraper')
    p.add_argument('--base-dir', dest='base_dir', default=DEFAULT_BASE_DIR,
                   help='Base directory to save CSVs (env IGRO_BASE_DIR overrides default)')
    p.add_argument('--dry-run', dest='dry_run', action='store_true',
                   help='Run a short dry-run: process one registration office, one village and one plot; skip writes/beeps')
    args = p.parse_args()
    return args

args = parse_args()
base_dir = args.base_dir

DRY_RUN = bool(getattr(args, 'dry_run', False))

# Guard winsound import (Windows-only). scripts historically imported winsound.
try:
    import winsound  # type: ignore
except Exception:
    winsound = None


s = requests.session()
headers={'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
regoff_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetRegoffice"
vil_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetVillage"
plot_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetPlotDtl"
ksmplt_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetKismByPlot"
mrval_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetMRVal"
initLists()
ctr, fctr  = 0, 0

DistId = input("Enter district ID:\t")
# DistId = 10
findRegOffs(DistId)
RestrtCh = input("Restart from last savepoint? Enter 'y' or 'n'. ")
if RestrtCh=='n':timecheck.constrfind(RegId)
if RestrtCh=='y':lim = retVill(DistId, RegName)

vil_payl = {'RegoffId':RegId}
vil_json = s.post(vil_api,json=vil_payl).json()
vctr = 0
for vil in vil_json['d']:
    vctr+=1
    if ctr==0 and RestrtCh=='y':        #breaker for resumefxn
        if vctr<=lim:
            progressbar.dispBar(vctr, lim, 30)
            continue
    if DRY_RUN and vctr>1:
        # dry-run: only process first village
        break
    print("\nReading data for", vil['VILL_ID'], "village under", RegName, "\b." )
    print("%i villages left to read." %int(len(vil_json['d'])-vctr))
    plot_payl = {'StrVillageId':vil['VILL_ID']}
    plot_resp = s.post(plot_api, json=plot_payl)
    if plot_resp.status_code == 200:
        plot_json = plot_resp.json()
    else:
        print("Unable to read data for village", vil['VILL_NAME'], "from", RegName, end=".\n")
        continue
    plot.json()
    pctr = 0
    for plot in plot_json['d']:
        st = time.time()
        ctr+=1; pctr+=1
        if DRY_RUN and pctr>1:
            # dry-run: only process first plot
            break
        ksmplt_payl = {'plotId':plot['One'], 'VillageId':vil['VILL_ID']}
        try:
            ksmplt_json = s.post(ksmplt_api, json=ksmplt_payl).json()
            ksm = ksmplt_json['d'][0]['PLOTCAT_TYPE']
            if len(ksmplt_json['d'])>1:
                ksm = "Multiple kisams found"
        except:
            ksm = "No Kisam found"
        mrval_payl = {'Dist':DistId, 'RegoffId':RegId, 'village':vil['VILL_ID'], 'Plot':plot['One'], 'Area':'1', 'Unit': '1', 'unitTest':'Acre'}
        try:
            mrval_json = s.post(mrval_api, json=mrval_payl).json()
            mrval = mrval_json['d'].split("@$")[1]
        except:
            mrval = "error"
            dt = "error"
            txndt = "error"
        else:
            try:
                dt = mrval_json['d'].split("@$")[6]
                txndt = mrval_json['d'].split("@$")[7]
            except:
                dt = "error"
                txndt = "error"
        dists.append(DistId)
        regoffs.append(RegId)
        vils.append(vil['VILL_ID'])
        plots.append(plot['One'])
        kisms.append(ksm)
        mrvals.append(mrval)
        dts.append(dt)
        txndts.append(txndt)
        if pctr%10==0:print("Read", pctr, "of", len(plot_json['d']), "values.", end='\r')
        if RestrtCh=='n':timecheck.estTimeRemain(st, ctr)
    else:    
        if vctr%50==0:       
            ss = time.time()
            df = pd.DataFrame({'District':dists, 'RegistrationOff':regoffs, 'Village':vils, 'PlotID':plots, 'Kisam':kisms, 'Value':mrvals, 'Date':dts, 'TransactionDate':txndts})
            loc = os.path.join(base_dir,str(DistId),RegName)
            if not DRY_RUN:
                if not os.path.exists(loc):os.makedirs(loc)
                df.to_csv(os.path.join(loc,"{}_{}.csv".format(RegName, fctr+1))); fctr+=1
            else:
                print("DRY-RUN: skipped file write for batch")
            ff = time.time()
            print("\nSaving directory to", loc, "took %.4f seconds." %(ff-ss), end=".\n")
            initLists()

df = pd.DataFrame({'District':dists, 'RegistrationOff':regoffs, 'Village':vils, 'PlotID':plots, 'Kisam':kisms, 'Value':mrvals, 'Date':dts, 'TransactionDate':txndts})
loc = os.path.join(base_dir,str(DistId),RegName)
if not DRY_RUN:
    if not os.path.exists(loc):os.makedirs(loc)
    df.to_csv(os.path.join(loc,"{}_rem.csv".format(RegName)), mode='a')
    print("Saved directory to", loc, end=".\n")
    for i in range(8):
        try:
            winsound.Beep(550, 750)
        except Exception:
            pass
else:
    print("DRY-RUN: skipped final write and notification beep(s)")