"""Pull all jobs since FY22-start and the customer id->name map. Save to data/.
Jobs carry customerId, businessUnitId, completedOn, total, invoiceId, jobStatus."""
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
    return {"Authorization":f"Bearer {tok}","ST-App-Key":env["SERVICETITAN_APP_KEY"],"User-Agent":UA,"Accept":"application/json"}
def get(path,hdrs):
    req=urllib.request.Request(BASE+path,headers=hdrs)
    return json.load(urllib.request.urlopen(req,timeout=90))

hdrs=client()
# --- Jobs since 2021-07-01 ---
jobs=[]; page=1
while True:
    r=get(f"/jpm/v2/tenant/{T}/jobs?modifiedOnOrAfter=2021-07-01T00:00:00&page={page}&pageSize=5000",hdrs)
    data=r.get("data",[])
    jobs.extend(data)
    print(f"jobs page {page}: +{len(data)} total={len(jobs)} hasMore={r.get('hasMore')}",flush=True)
    if not r.get("hasMore") or not data:
        break
    page+=1
json.dump(jobs,open("/root/.hermes/pages/clv-report/data/jobs_5yr.json","w"))
print("JOBS SAVED",len(jobs),flush=True)

# --- Customers id->name (+ createdOn) ---
cust=[]; page=1
while True:
    r=get(f"/crm/v2/tenant/{T}/customers?page={page}&pageSize=5000",hdrs)
    data=r.get("data",[])
    cust.extend(data)
    print(f"customers page {page}: +{len(data)} total={len(cust)} hasMore={r.get('hasMore')}",flush=True)
    if not r.get("hasMore") or not data:
        break
    page+=1
json.dump(cust,open("/root/.hermes/pages/clv-report/data/customers.json","w"))
print("CUSTOMERS SAVED",len(cust),flush=True)