import json, time, requests
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
URLS = {
 "bhavcopy": "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261109_F_0000.csv.zip",
 "indices": "https://nsearchives.nseindia.com/content/indices/ind_close_all_09112026.csv",
 "pr_zip": "https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR091126.zip",
 "equity_l": "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
 "total_market": "https://nsearchives.nseindia.com/content/indices/ind_niftytotalmarket_list.csv",
 "sme_l": "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv",
 "bulk": "https://nsearchives.nseindia.com/content/equities/bulk.csv",
 "nsdl": "https://www.fpi.nsdl.co.in/web/StaticReports/Fortnightly_Sector_wise_FII_Investment_Data/FIIInvestSector_Oct312026.html",
 "yahoo": "https://query1.finance.yahoo.com/v8/finance/chart/RELIANCE.NS?range=5d&interval=1d",
}
out = {"ip": None, "rounds": []}
try: out["ip"] = requests.get("https://ipinfo.io/json", timeout=15).json()
except Exception as e: out["ip"] = str(e)
for rnd in range(3):
    r = {}
    for k, u in URLS.items():
        t = time.time()
        try:
            x = requests.get(u, headers=UA, timeout=40)
            r[k] = [x.status_code, len(x.content), round(time.time() - t, 1)]
        except Exception as e:
            r[k] = ["ERR", type(e).__name__, round(time.time() - t, 1)]
    t = time.time()
    try:
        body = {"match": {"mrktCapf": {"g": 1000}}, "sortBy": "mrktCapf", "sortOrder": -1, "project": ["mrktCapf", "forInstHldng3M"], "offset": 0, "count": 3000, "sids": []}
        x = requests.post("https://api.tickertape.in/screener/query", json=body, headers={**UA, "Content-Type": "application/json", "accept-version": "8.14.0"}, timeout=60)
        r["tickertape"] = [x.status_code, len(x.content), round(time.time() - t, 1)]
    except Exception as e:
        r["tickertape"] = ["ERR", type(e).__name__, round(time.time() - t, 1)]
    out["rounds"].append(r); time.sleep(20)
json.dump(out, open("result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
