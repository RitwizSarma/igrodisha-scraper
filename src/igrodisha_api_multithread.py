import os
import pandas as pd
import requests, time
import argparse
from multiprocessing.pool import ThreadPool
from helpers_multithread import *

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
# if RestrtCh=='n':timecheck.constrfind(RegId)
if RestrtCh=='y':lim = retVill(DistId, RegName)
vil_payl = {'RegoffId':RegId}
vil_json = s.post(vil_api,json=vil_payl).json()
vctr, n_retry = 0, 0
tm = 0

for vil in vil_json['d']:
    ReentryAllowed = True
    if ctr==0 and RestrtCh=='y':        #breaker for resumefxn
        if vctr<=lim:
            vctr+=1
            continue

    st = time.time()
    while ReentryAllowed:
        ReentryAllowed = False
        print("Reading data for", vil['VILL_ID'], "village under", RegName, "\b." )
        print("%i villages left to read." %int(len(vil_json['d'])-vctr))
        curr_vil = vil['VILL_ID']
        plot_payl = {'StrVillageId':curr_vil}
        plot_json = s.post(plot_api, json=plot_payl).json()
        plot_list = [plot['One'] for plot in plot_json['d']]
        if DRY_RUN:
            # only test one plot in dry-run
            plot_list = plot_list[:1]
        try:
            with ThreadPool(6) as pool:
                for strn in pool.map(scrapePlot, plot_list):
                    mrval_strs.append(strn)
                    ctr+=1
            ReentryAllowed = False
        except:
            if n_retry<3:
                ReentryAllowed = True
                n_retry+=1
            else:
                n_retry = 0
                break
    vctr+=1
    tm = time.time() - st
    if len(mrval_strs)!=0:print("Per-iteration time is %.5f" %(tm/len(mrval_strs)))
    if vctr%50==0:
        if not DRY_RUN:
            fileDump(mrval_strs)
        else:
            print("DRY-RUN: skipped file dump")
        



