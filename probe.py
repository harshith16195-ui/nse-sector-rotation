import io, json, time, zipfile, traceback, requests
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
out = {}
def t(name, fn):
    t0 = time.time()
    try: out[name] = {"ok": fn(), "s": round(time.time() - t0, 1)}
    except Exception as e: out[name] = {"err": f"{type(e).__name__}: {e}"[:300], "s": round(time.time() - t0, 1)}
def yf_prices():
    import yfinance as yf
    df = yf.download(["^CRSLDX", "^NSEI", "^NSMIDCP", "NOVARTIND.BO", "ABCOTS.NS", "ABCOTS.BO"], period="1mo", auto_adjust=True, progress=False, threads=True)
    c = df["Close"]; return {k: [int(c[k].notna().sum()), None if c[k].dropna().empty else round(float(c[k].dropna().iloc[-1]), 2), str(c[k].dropna().index[-1].date()) if c[k].notna().any() else None] for k in c.columns}
def yf_max():
    import yfinance as yf
    df = yf.download(["^CRSLDX", "NOVARTIND.BO"], period="max", auto_adjust=True, progress=False)
    return {k: int(df["Close"][k].notna().sum()) for k in df["Close"].columns}
def yf_shares():
    import yfinance as yf
    return {s: float(yf.Ticker(s).fast_info["shares"]) for s in ["RELIANCE.NS", "NOVARTIND.BO"]}
def yf_info():
    import yfinance as yf
    i = yf.Ticker("INFY.NS").info; return [i.get("sector"), i.get("industry"), i.get("sharesOutstanding")]
def yf_splits():
    import yfinance as yf
    return len(yf.Ticker("TCS.NS").splits)
def bse():
    h = {**UA, "Referer": "https://www.bseindia.com/"}
    r = requests.get("https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_20261109_F_0000.CSV", headers=h, timeout=40)
    lines = r.text.splitlines()
    return [r.status_code, len(r.content), lines[0][:300], [l[:200] for l in lines if ",500672," in l or "NOVARTIND" in l][:2]]
def pr_zip():
    r = requests.get("https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR091126.zip", headers=UA, timeout=60)
    z = zipfile.ZipFile(io.BytesIO(r.content)); names = z.namelist()
    m = [n for n in names if "mcap" in n.lower()]
    head = z.read(m[0]).decode("latin1").splitlines()[:4] if m else None
    return {"names": names, "mcap_head": head}
def history_speed():
    days = ["03JAN2011","04JAN2011","05JAN2011","06JAN2011","07JAN2011","10JAN2011","11JAN2011","12JAN2011","13JAN2011","14JAN2011",
            "02MAR2015","03MAR2015","04MAR2015","05MAR2015","09MAR2015","10MAR2015","11MAR2015","12MAR2015","13MAR2015","16MAR2015",
            "01AUG2019","02AUG2019","05AUG2019","06AUG2019","07AUG2019","08AUG2019","09AUG2019","13AUG2019","14AUG2019","16AUG2019",
            "03JAN2006","04JAN2006","05JAN2006","06JAN2006","09JAN2006","10JAN2006","12JAN2006","13JAN2006","16JAN2006","17JAN2006"]
    def one(d):
        u = f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{d[5:]}/{d[2:5]}/cm{d}bhav.csv.zip"
        try: return requests.get(u, headers=UA, timeout=40).status_code
        except Exception as e: return type(e).__name__
    with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, days))
    from collections import Counter
    return dict(Counter(map(str, res)))
for n, f in [("yf_prices", yf_prices), ("yf_max", yf_max), ("yf_shares", yf_shares), ("yf_info", yf_info), ("yf_splits", yf_splits), ("bse_bhavcopy", bse), ("nse_pr_zip", pr_zip), ("history_speed_40_days", history_speed)]:
    t(n, f)
json.dump(out, open("result.json", "w"), indent=1); print(json.dumps(out, indent=1))
