"""Resume report-295 monthly pull. Re-auths token on every attempt (401 after 15min).
Loads existing incremental data, continues from first missing month."""
import json, os, time, urllib.request, re, datetime
T="3306271893"; BASE="https://api.servicetitan.io"; UA="hermes-agent/1.0"
OUT="/root/.hermes/pages/clv-report/data/monthly_revenue_by_bu.json"
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
# load existing
result={}
if os.path.exists(OUT):
    try: result=json.load(open(OUT))
    except: pass
# build all months
MONTHS=[]
d=datetime.date(2024,10,1)
while d<=datetime.date(2026,8,31):
    y,m=d.year,d.month
    e=datetime.date(y+1,1,1) if m==12 else datetime.date(y,m+1,1)
    MONTHS.append((f"{y:04d}-{m:02d}", d.isoformat(), e.isoformat()))
    d=e
for label,f,t in MONTHS:
    if result.get(label) is not None:   # already have it (list or None placeholder)
        continue
    ok=False
    for attempt in range(8):
        hdrs=client()   # fresh token each retry
        try:
            resp=urllib.request.urlopen(urllib.request.Request(
                BASE+f"/reporting/v2/tenant/{T}/report-category/business-unit-dashboard/reports/295/data",
                data=json.dumps({"parameters":[{"name":"From","value":f},{"name":"To","value":t}]}).encode(),
                headers=hdrs),timeout=180)
            r=json.loads(resp.read())
            rows=r.get("values",r.get("data",[]))
            result[label]=rows
            print(label,"rows:",len(rows),flush=True)
            ok=True
            break
        except urllib.error.HTTPError as e:
            body=e.read().decode()
            if e.code==429:
                m=re.search(r"Try again in (\d+)",body)
                delay=int(m.group(1))+2 if m else 70
                print(label,"429 wait",delay,flush=True)
                time.sleep(min(delay,85)); continue
            print(label,"HTTP",e.code,body[:100],flush=True)
            time.sleep(3); continue
        except Exception as ex:
            print(label,"ERR",repr(ex),flush=True); time.sleep(3); continue
    if not ok:
        result[label]=None
    json.dump(result,open(OUT,"w"))
    time.sleep(60)
print("DONE",len([k for k,v in result.items() if v]),"months saved",flush=True)