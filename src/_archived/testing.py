import requests, time, os
import pandas as pd
from multiprocessing.pool import ThreadPool

class progressbar():
    '''Default progress bar used for multiple functions.'''
    def dispBar(iter, constr,  res):
        pct = 100 * (iter/constr)
        blno = int((pct/100) * res)
        bl_str = "▒" * blno
        if iter != constr: line_str = "_" * (res-blno)
        else: line_str = ""
        print(bl_str+line_str, "%.3f percent done..." %pct, end='\r')

DistId = 1
RegId = 177
base_dir = "C:/Codes/Try"
RegName = "KISHORENAGAR"

vils, plots = [], []
kisms, mrvals, dts, txndts = [], [], [], []


def rand(plot):
    global vil_iter, RegId, DistId
    ksmplt_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetKismByPlot"
    ksmplt_payl = {'plotId':plot, 'VillageId':vil_iter}
    try:
        ksmplt_json = s.post(ksmplt_api, json=ksmplt_payl).json()
        ksm = ksmplt_json['d'][0]['PLOTCAT_TYPE']
        if len(ksmplt_json['d'])>1:
            ksm = "Multiple kisams found"
    except:
        ksm = "No Kisam found"
    
    mrval_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetMRVal"
    mrval_payl = {'Dist': DistId, 'RegoffId': RegId,'village': vil_iter,'Plot': plot,'Area': "1",'Unit': "1",'unitTest': "Acre"}
    mrval_json = s.post(mrval_api, json=mrval_payl).json()

    return mrval_json['d']+"@$"+str(ksm)+"@$"+str(vil_iter)+"@$"+str(plot)

def initLists():
    global dists, regoffs, vils, plots, ctr
    global kisms, mrvals, dts, txndts , mrval_strs
    dists, regoffs, vils, plots = [], [], [], []
    kisms, mrvals, dts, txndts = [], [], [], []
    mrval_strs = []
    ctr = 0

def fileDump(mrval_st):
    global DistId, RegId, ctr, fctr
    ss = time.time()
    print(ctr)
    dists = [DistId for i in range(ctr)]
    regoffs = [RegId for i in range(ctr)]
    for strn in mrval_st:
        plot = strn.split("@$")[-1]
        vill = strn.split("@$")[-2]
        ksm = strn.split("@$")[-3]
        try:
            mrval = strn.split("@$")[1]
        except:
            mrval = "error"
            dt = "error"
            txndt = "error"
        else:
            try:
                dt = strn.split("@$")[6]
                txndt = strn.split("@$")[7]
            except:
                dt = "error"
                txndt = "error"
        vils.append(vill)
        plots.append(plot)
        kisms.append(ksm)
        mrvals.append(mrval)
        dts.append(dt)
        txndts.append(txndt)
    print(len(dists), len(regoffs),len(vils),len(plots),len(kisms),len(mrvals),len(dts),len(txndts))
    df = pd.DataFrame({'District':dists, 'RegistrationOff':regoffs, 'Village':vils, 'PlotID':plots, 'Kisam':kisms, 'Value':mrvals, 'Date':dts, 'TransactionDate':txndts})
    loc = os.path.join(base_dir,str(DistId),"Try/")
    if not os.path.exists(loc):os.makedirs(loc)
    df.to_csv(os.path.join(loc,"{}_{}.csv".format(RegName, fctr+1))); fctr+=1
    ff = time.time()
    print("\nSaving directory to", loc, "took %.4f seconds." %(ff-ss), end=".\n")
    initLists()



s = requests.session()
villls = [1770003, 1770004, 1770005, 1770006]
vctr = 0
n_retry, fctr = 0, 0
initLists()

for vil in villls:
    entryAllowed = True
    progressbar.dispBar(vctr, len(villls), 50)
    while entryAllowed:
        entryAllowed = False                                
        plot_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetPlotDtl"
        plot_payl = {'StrVillageId':vil}
        plot_json = s.post(plot_api, json=plot_payl).json()
        plot_list = [plot['One'] for plot in plot_json['d']]
        # plot_list = plot_list[-1500:]
        vil_iter = vil
        st = time.time()
        try:
            with ThreadPool(7) as pool:
                for strn in pool.map(rand, plot_list):
                    mrval_strs.append(strn)
                    ctr+=1
            entryAllowed = False
        except ConnectionError:
            if n_retry<3:
                entryAllowed = True
                n_retry+=1
            else:
                n_retry = 0
                break
    vctr+=1

    if vctr%2==0:fileDump(mrval_strs)





        # ss = time.time()
        # print(ctr)
        # dists = [DistId for i in range(len(mrval_strs))]
        # regoffs = [RegId for i in range(len(mrval_strs))]
        # for strn in mrval_strs:
        #     plot = strn.split("@$")[-1]
        #     vill = strn.split("@$")[-2]
        #     ksm = strn.split("@$")[-3]
        #     try:
        #         mrval = strn.split("@$")[1]
        #     except:
        #         mrval = "error"
        #         dt = "error"
        #         txndt = "error"
        #     else:
        #         try:
        #             dt = strn.split("@$")[6]
        #             txndt = strn.split("@$")[7]
        #         except:
        #             dt = "error"
        #             txndt = "error"
        #     vils.append(vill)
        #     plots.append(plot)
        #     kisms.append(ksm)
        #     mrvals.append(mrval)
        #     dts.append(dt)
        #     txndts.append(txndt)

        # print(len(dists), len(regoffs),len(vils),len(plots),len(kisms),len(mrvals),len(dts),len(txndts))
        # df = pd.DataFrame({'District':dists, 'RegistrationOff':regoffs, 'Village':vils, 'PlotID':plots, 'Kisam':kisms, 'Value':mrvals, 'Date':dts, 'TransactionDate':txndts})
        # loc = os.path.join(base_dir,str(DistId),"Try/")
        # if not os.path.exists(loc):os.makedirs(loc)
        # df.to_csv(os.path.join(loc,"{}_{}.csv".format(RegName, fctr+1))); fctr+=1
        # ff = time.time()
        # print("\nSaving directory to", loc, "took %.4f seconds." %(ff-ss), end=".\n")
        # initLists()





# mrval_api = "https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetMRVal"
# mrval_payl = {'Dist': "1", 'RegoffId': "177",'village': "1770003",'Plot': '106','Area': "1",'Unit': "1",'unitTest': "Acre"}
# mrval_json = s.post(mrval_api, json=mrval_payl).json()
# print(mrval_json['d'])


# print(plots_list)