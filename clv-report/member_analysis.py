import json
from collections import defaultdict
from datetime import datetime as D

mem = json.load(open("/root/.hermes/pages/clv-report/data/memberships.json"))
cust_rev = json.load(open("/root/.hermes/pages/clv-report/data/bubble_top.json"))
jobs = json.load(open("/root/.hermes/pages/clv-report/data/jobs_5yr.json"))

def dt(s):
    try: return D.fromisoformat(s.replace("Z", "+00:00")[:19])
    except: return None

active_ids = set(m.get("customerId") for m in mem if m.get("status") == "Active")
ever_ids = set(m.get("customerId") for m in mem)
print("active member customer ids:", len(active_ids), "| ever-member ids:", len(ever_ids))

brand_split_m = defaultdict(lambda: [0.0, 0, 0])
brand_split_n = defaultdict(lambda: [0.0, 0, 0])
live_ids = set()
for b, c in cust_rev.items():
    # c is a list of {cid,rev,orders,aov}
    for r in c:
        cid = int(r["cid"]); live_ids.add(cid)
        groups = (brand_split_m if cid in active_ids else brand_split_n)
        groups[b][0] += r["rev"]; groups[b][1] += 1; groups[b][2] += r["orders"]

m_rev = sum(v[0] for v in brand_split_m.values()); m_c = sum(v[1] for v in brand_split_m.values()); m_o = sum(v[2] for v in brand_split_m.values())
n_rev = sum(v[0] for v in brand_split_n.values()); n_c = sum(v[1] for v in brand_split_n.values()); n_o = sum(v[2] for v in brand_split_n.values())

print("LIVE WINDOW (Nov24-present):")
print(f"  MEMBERS:     {m_c} customers | ${m_rev:,.0f} rev | {m_o} orders | AOV ${m_rev/m_o:,.0f} | orders/cust {m_o/m_c:.2f}")
print(f"  NON-MEMBERS: {n_c} customers | ${n_rev:,.0f} rev | {n_o} orders | AOV ${n_rev/n_o:,.0f} | orders/cust {n_o/n_c:.2f}")
print(f"  members {100*m_c/(m_c+n_c):.1f}% of customers, {100*m_rev/(m_rev+n_rev):.1f}% of revenue")

active_live = live_ids & active_ids
print("active members who appear in live-window invoices:", len(active_live), "of", len(active_ids))

# 5yr new/repeat cross-tab
BU_ID_BRAND = {12602939:"Air Con",12602940:"Air Con",212505761:"Air Con",212505762:"Air Con",
12602941:"Plumbing/Gas",12602942:"Plumbing/Gas",212505765:"Plumbing/Gas",212505766:"Plumbing/Gas",
446820082:"Trades",446820229:"Trades",12602943:"Electrical",12602944:"Electrical",212505763:"Electrical",212505764:"Electrical",
12602945:"AEP",12602946:"AEP",212505767:"AEP",212505768:"AEP",438216198:"Roofing",438217837:"Roofing",438218186:"Roofing",438215183:"Roofing",
439465801:"Renovations",439465691:"Renovations",451220780:"Trades",451221451:"Trades"}
bycust = defaultdict(list)
for j in jobs:
    d = dt(j.get("completedOn"))
    if d and d.year > 2000 and D(2021,7,1) <= d <= D(2026,6,30,23,59,59):
        bycust[j.get("customerId")].append(d)
m_new = m_rep = n_new = n_rep = 0
for cid, c in bycust.items():
    rep = 1 if len(c) > 1 else 0
    if cid in active_ids:
        if rep: m_rep += 1
        else: m_new += 1
    else:
        if rep: n_rep += 1
        else: n_new += 1
print("5yr window new/repeat cross-tab:")
print(f"  Members: new(1job)={m_new} repeat(>1)={m_rep} repeat%={100*m_rep/(m_new+m_rep):.1f}")
print(f"  Non-mem: new={n_new} repeat={n_rep} repeat%={100*n_rep/(n_new+n_rep):.1f}")

from collections import Counter
mt = Counter(m.get("membershipTypeId") for m in mem if m.get("status") == "Active")
print("active type mix:", dict(mt))  # 263515228=Gold, 263515483=Platinum

json.dump({"active_ids": sorted(active_ids), "ever_ids": sorted(ever_ids)},
          open("/root/.hermes/pages/clv-report/data/member_ids.json", "w"))
print("saved member_ids.json")