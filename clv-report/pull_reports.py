"""Pull report 295 (Revenue by BU) per financial year + full-window, save JSON.
Respects ~1/min reporting rate limit via sleeps between calls."""
import json, os, time, urllib.request
T="3306271893"; BASE="https://api.servicetitan.io"; UA="hermes-agent/1.0"
def load_env():
    e={}
    for line in open("/root/.hermes/secrets/servicetitan.env"):
        line=line.strip()
        if line and not line.startswith("#") and "=" in line:
            k,_,v=line.partition("="); e[k.strip()]=v.strip().strip('"').strip("'")
    return e
env=load_env()
def client():
    import urllib.parse
    data=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":env["SERVICETITAN_CLIENT_ID"],"client_secret":env["SERVICETITAN_CLIENT_SECRET"]}).encode()
    req=urllib.request.Request("https://auth.servicetitan.io/connect/token",data=data,headers={"Content-Type":"application/x-www-form-urlencoded","User-Agent":UA})
    tok=json.load(urllib.request.urlopen(req,timeout=30))["access_token"]
    return {"Authorization":f"Bearer {tok}","ST-App-Key":env["SERVICETITAN_APP_KEY"],"User-Agent":UA,"Content-Type":"application/json"}
def post(path,body,hdrs):
    req=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers=hdrs)
    return json.load(urllib.request.urlopen(req,timeout=180))
OUT="/root/.hermes/pages/clv-report/data/revenue_by_bu.json"
windows={"FY24":["2023-07-01","2024-06-30"],"FY25":["2024-07-01","2025-06-30"],"FY26":["2025-07-01","2026-06-30"],"FY22_26":["2021-07-01","2026-06-30"]}
hdrs=client()
result={}
try:
    for fy,(f,t) in windows.items():
        for attempt in range(4):
            try:
                resp=post(f"/reporting/v2/tenant/{T}/report-category/business-unit-dashboard/reports/295/data",
                          {"parameters":[{"name":"From","value":f},{"name":"To","value":t}]},hdrs)
                rows=resp.get("values",resp.get("data",[]))
                result[fy]=rows
                print(fy,"rows:",len(rows),flush=True)
                break
            except urllib.error.HTTPError as e:
                body=e.read().decode()
                if e.code==429:
                    import re
                    m=re.search(r"Try again in (\d+)",body)
                    delay=int(m.group(1))+2 if m else 70
                    print(f"{fy} 429, wait {delay}s",flush=True)
                    time.sleep(min(delay,80)); continue
                print(fy,"HTTP",e.code,body[:150],flush=True); result[fy]=None; break
        time.sleep(65)  # spacing between reports
    json.dump(result,open(OUT,"w"))
    print("SAVED",OUT,flush=True)
except Exception as ex:
    print("FATAL",repr(ex),flush=True)
    json.dump(result,open(OUT,"w"))
