#!/usr/bin/env python3
"""Renders the CLV Financial Report for aba TRADES as a single self-contained
HTML page (inline CSS + hand-rolled SVG charts, no external JS). Reads the
ServiceTitan pulls saved in ./data/. On-brand per client-design skill."""
import json, os, datetime, xml.sax.saxutils as esc
D = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(D, "data")

def load(name, default):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    try: return json.load(open(p))
    except: return default

def money(x, dec=0):
    return "${:,.{}f}".format(x, dec) if x is not None else "—"

# ---------------------------------------------------------------------------
# Brand palette (deep accents from client-design)
BRANDS = ["Plumbing/Gas","Air Con","AEP","Electrical","Roofing","Renovations","Trades"]
ACCENT = {"Plumbing/Gas":"#94BE8C","Air Con":"#58A4AE","AEP":"#0B1D3B",
          "Electrical":"#DC7E49","Roofing":"#A0AFD9","Renovations":"#E57D7D","Trades":"#7789A7"}

def brand_html(b):
    return f'<span style="color:{ACCENT.get(b,"#1D3B6D")};font-weight:700">{b}</span>'

# ---------------------------------------------------------------------------
# Data
monthly = load("monthly_revenue_by_bu.json", {})   # {YYYY-MM: [rows]} rows=[name,totalSales,totalRev,...]
rev_by_bu = load("revenue_by_bu.json", {})
cust_rev = load("bubble_top.json", {})              # {brand: [{cid,rev,orders,aov}]}
jobs_data = load("jobs_5yr.json", [])

BU_ID_BRAND = {
 12602939:"Air Con",12602940:"Air Con",212505761:"Air Con",212505762:"Air Con",
 12602941:"Plumbing/Gas",12602942:"Plumbing/Gas",212505765:"Plumbing/Gas",212505766:"Plumbing/Gas",
 446820082:"Trades",446820229:"Trades",
 12602943:"Electrical",12602944:"Electrical",212505763:"Electrical",212505764:"Electrical",
 12602945:"AEP",12602946:"AEP",212505767:"AEP",212505768:"AEP",
 438216198:"Roofing",438217837:"Roofing",438218186:"Roofing",438215183:"Roofing",
 439465801:"Renovations",439465691:"Renovations",
 451220780:"Trades",451221451:"Trades"}

def dt(s):
    if not s: return None
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")[:19])
    except: return None

# ---- New vs repeat (5-yr window FY22-26 from jobs) ----
from collections import defaultdict
bybrand = defaultdict(lambda: defaultdict(list))
for j in jobs_data:
    d = dt(j.get("completedOn"))
    if not d or d.year < 2001 or not (datetime.datetime(2021,7,1) <= d <= datetime.datetime(2026,6,30,23,59,59)):
        continue
    b = BU_ID_BRAND.get(j.get("businessUnitId"), "Unassigned")
    bybrand[b][j.get("customerId")].append(d)
cust_stats = {}
for b, c in bybrand.items():
    new = sum(1 for v in c.values() if len(v)==1)
    rep = sum(1 for v in c.values() if len(v)>1)
    cust_stats[b] = {"distinct":len(c),"new":new,"repeat":rep,
                     "repeat_pct":100*rep/len(c) if c else 0}

# ---- Revenue trend: aggregate monthly report 295 rows by brand ----
# monthly rows: [Name, TotalSales, TotalRevenue(col2), OnlineEstimate, RevPerHour]
def rep_rows_to_brand(rows):
    # returns {brand: totalRevenue}
    out = defaultdict(float)
    BU2B = {
     "aba-AC-Quoter":"Air Con","aba-AC-Installer":"Air Con","aba-AC-Install-Afterhours":"Air Con","aba-AC-Quote-Afterhours":"Air Con",
     "aba-Plumbing-Quoter":"Plumbing/Gas","aba-Plumbing-Installer":"Plumbing/Gas","aba-Plumbing-Install-Afterhours":"Plumbing/Gas","aba-Plumbing-Quote-Afterhours":"Plumbing/Gas",
     "AEP-Plumbing-Quoter":"AEP","AEP-Plumbing-Installer":"AEP","AEP-Plumbing-Install-Afterhours":"AEP","AEP-Plumbing-Quote-Afterhours":"AEP",
     "aba-Electrical-Quoter":"Electrical","aba-Electrical-Installer":"Electrical","aba-Ele-Install-Afterhours":"Electrical","aba-Ele-Quote-Afterhours":"Electrical",
     "aba-Roofing-Quote":"Roofing","aba-Roofing-Quote-Afterhours":"Roofing","aba-Roofing-Install":"Roofing","aba-Roofing-Install-Afterhours":"Roofing",
     "aba-Renovation-Quoter":"Renovations","aba-Renovations-Installer":"Renovations",
     "aba-Commercial-Quoting":"Trades","aba-Commercial-Install":"Trades","aba-TRADES-Quoter":"Trades","aba-TRADES-Installer":"Trades",
     "aba-Membership":"Memberships","aba-Membership-Quote":"Memberships"}
    for r in rows:
        if not r: continue
        b = BU2B.get(r[0])
        if b:
            out[b] += r[2] or 0
    return dict(out)

months = sorted(monthly.keys())
trend = {m: rep_rows_to_brand(monthly[m]) for m in months}  # {month: {brand: rev}}
trend_all = []
for m in months:
    row = {"month":m}
    row.update(trend[m])
    trend_all.append(row)

# percentages for labeling the no-data window
FIRST_GOOD = months[0] if months else None

# ---------------------------------------------------------------------------
# SVG helpers
def svg_line_chart(rows, brands, title, height=340, color_by=None):
    """rows: list of {month, brand:val}. Grouped/stacked? -> stacked area for brands."""
    color_by = color_by or ACCENT
    months_all = [r["month"][2:].replace("-","/") for r in rows]
    n = len(rows)
    W, H, padL, padB, padT, padR = 960, height, 70, 42, 28, 16
    plotW, plotH = W-padL-padR, H-padT-padB
    vals = [rows[i][b] or 0 for i in range(n) for b in brands]
    # current-brand rev can be absent -> treat 0
    for i in range(n):
        for b in brands:
            rows[i].setdefault(b, 0)
    maxv = max(vals) if vals else 1
    maxv = maxv * 1.12
    def X(i): return padL + plotW*i/max(n-1,1)
    def Y(v): return padT + plotH - plotH*v/maxv
    # horizontal gridlines
    g = []
    for gi in range(0, 5):
        yv = maxv*gi/4
        y = Y(yv)
        g.append(f'<line x1="{padL}" y1="{y:.1f}" x2="{W-padR}" y2="{y:.1f}" stroke="#D3D4DA" stroke-width="1"/>'
                 f'<text x="{padL-8}" y="{y+4:.1f}" font-size="11" fill="#1D3B6D" text-anchor="end">{int(yv//1000)}k</text>')
    # area series
    svg = []
    # reverse so biggest on top
    for b in reversed(brands):
        pts = " ".join(f"{X(i):.1f},{Y(rows[i][b]):.1f}" for i in range(n))
        fill = color_by.get(b,"#1D3B6D")
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{fill}" stroke-width="2.5" opacity="0.9"/>')
        svg.append(f'<polyline points="{padL},{padT+plotH} {pts} {W-padR},{padT+plotH}" fill="{fill}" stroke="none" opacity="0.12"/>')
    # x labels
    step = max(1, n//12)
    xlab = "".join(f'<text x="{X(i):.1f}" y="{H-14}" font-size="10" fill="#6b7280" text-anchor="middle">{m}</text>'
                   for i,m in enumerate(months_all) if i%step==0 or i==n-1)
    legend = "".join(f'<rect x="{x}" y="{H-40}" width="11" height="11" rx="2" fill="{ACCENT.get(b,"#1D3B6D")}"/><text x="{x+15}" y="{H-30}" font-size="11" fill="#1D3B6D">{b}</text>'
                     for x,b in zip(range(40,40+len(brands)*130,130), brands))
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="{padL}" y="18" font-size="15" font-weight="700" fill="#1D3B6D">{esc.escape(title)}</text>'
            + "".join(g) + "".join(svg) + xlab + f'<g>{legend}</g></svg>')

def svg_bubble(cust_list, brand, metric, width=960, height=420):
    """Bubble chart: x = customer index (by revenue desc), y = AOV or REV, r = rev/orders."""
    if not cust_list: return "<p>No data</p>"
    if metric == "aov":
        yy = lambda r: r["aov"]; title = f"Average order value per customer — {brand}"
        ylab = "AOV ($)"
    else:
        yy = lambda r: r["rev"]; title = f"Total revenue per customer — {brand}"
        ylab = "Total revenue ($)"
    W,H,padL,padB,padT,padR = width,height,70,48,40,20
    plotW,plotH = W-padL-padR, H-padT-padB
    top = [c for c in cust_list if c["rev"]>0][:80]  # top 80 by revenue
    if not top: return "<p>No customers with revenue</p>"
    maxv = max((yy(c) for c in top), default=1)*1.1
    maxr = max(c["rev"] for c in top)
    def X(i): return padL + plotW*i/max(len(top)-1,1)
    def Y(v): return padT + plotH - plotH*v/maxv
    def R(c): return max(3.0, 18.0*(c["rev"]/maxr)**0.5)
    g=[f'<line x1="{padL}" y1="{Y(maxv*gi/4):.1f}" x2="{W-padR}" y2="{Y(maxv*gi/4):.1f}" stroke="#D3D4DA"/>'
       f'<text x="{padL-8}" y="{Y(maxv*gi/4)+4:.1f}" font-size="11" fill="#1D3B6D" text-anchor="end">{int(maxv*gi/4//1000)}k</text>'
       for gi in range(5)]
    bubbles="".join(f'<circle cx="{X(i):.1f}" cy="{Y(yy(c)):.1f}" r="{R(c):.1f}" fill="{ACCENT.get(brand,"#1D3B6D")}" opacity="0.65"><title>{c["cid"]} • {money(c["rev"])} • {"{:.0f}".format(c["orders"])} orders • AOV {money(c["aov"])}</title></circle>'
                    for i,c in enumerate(top))
    xlab=f'<text x="{padL+plotW/2}" y="{H-10}" font-size="11" fill="#6b7280" text-anchor="middle">Customers, largest by revenue →</text>'
    ylabt=f'<text x="-{padT+plotH/2}" y="14" font-size="11" fill="#6b7280" text-anchor="middle" transform="rotate(-90)">{ylab}</text>'
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="{padL}" y="22" font-size="15" font-weight="700" fill="#1D3B6D">{esc.escape(title)}</text>'
            + "".join(g) + bubbles + xlab + ylabt + "</svg>")

# ---------------------------------------------------------------------------
# Build the page
LOGO_URI = ""
try:
    LOGO_URI = open(os.path.join(DATA, "logo_badge_uri.txt")).read().strip()
except Exception:
    pass
member_split = load("member_brand_split.json", {})
REPORT_STAMP = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

SECTIONS = []

# Members vs non-members
def ms_steady(x):
    try: return float(x)
    except: return 0.0
m_total_cust = sum(int(v["m_cust"]) for v in member_split.values())
n_total_cust = sum(int(v["n_cust"]) for v in member_split.values())
m_total_rev = sum(ms_steady(v["m_rev"]) for v in member_split.values())
n_total_rev = sum(ms_steady(v["n_rev"]) for v in member_split.values())
m_total_ord = sum(int(v["m_orders"]) for v in member_split.values())
n_total_ord = sum(int(v["n_orders"]) for v in member_split.values())
m_aov = m_total_rev / m_total_ord if m_total_ord else 0
n_aov = n_total_rev / n_total_ord if n_total_ord else 0
m_freq = m_total_ord / m_total_cust if m_total_cust else 0
n_freq = n_total_ord / n_total_cust if n_total_cust else 0
share_cust = 100 * m_total_cust / (m_total_cust + n_total_cust) if (m_total_cust + n_total_cust) else 0
share_rev = 100 * m_total_rev / (m_total_rev + n_total_rev) if (m_total_rev + n_total_rev) else 0
kbars_m = '<div class="bubble-bar"><span class="bbar m"></span><span class="bbar n"></span></div>'
member_rows = ""
for b in BRANDS:
    if b not in member_split: continue
    v = member_split[b]
    mv, nv = ms_steady(v["m_aov"]), ms_steady(v["n_aov"])
    mc, nc = int(v["m_cust"]), int(v["n_cust"])
    mo, no = int(v["m_orders"]), int(v["n_orders"])
    mf = mo / mc if mc else 0
    nf = no / nc if nc else 0
    mr = ms_steady(v["m_rev"])
    row = (f'<tr><td>{brand_html(b)}</td>'
           f'<td>{mc}</td><td>{money(mr)}</td><td>{money(mv)}</td><td>{mf:.2f}</td>'
           f'<td>{nc}</td><td>{money(ms_steady(v["n_rev"]))}</td><td>{money(nv)}</td><td>{nf:.2f}</td></tr>')
    member_rows += row
SECTIONS.append(f"""
<section class="card">
  <h2>Members vs non-members</h2>
  <p class="note">Lifetime value of a member customer vs a non-member, over the live window (Nov 2024 → present). Members = customers with an active Gold/Platinum membership ({m_total_cust} distinct active-member customers, of 1,316 active across the whole base).</p>
  <div class="kpi-row">
    <div class="kpi"><div class="kn">Members</div><div class="kv">{money(m_total_rev)}</div><div class="ku">revenue · {m_total_cust} customers</div></div>
    <div class="kpi"><div class="kn">Member share</div><div class="kv">{share_cust:.0f}%</div><div class="ku">of customers · <b>{share_rev:.0f}%</b> of revenue</div></div>
    <div class="kpi"><div class="kn">Member AOV</div><div class="kv">{money(m_aov)}</div><div class="ku">vs non-member {money(n_aov)}</div></div>
    <div class="kpi"><div class="kn">Member freq</div><div class="kv">{m_freq:.2f}</div><div class="ku">orders/cust · non-memb. {n_freq:.2f}</div></div>
    <div class="kpi"><div class="kn">Non-members</div><div class="kv">{money(n_total_rev)}</div><div class="ku">revenue · {n_total_cust} customers</div></div>
  </div>
  <div class="tbl-wrap"><table><thead><tr><th>Business unit</th><th>Members</th><th>Member revenue</th><th>Member AOV</th><th>Memb. freq</th><th>Non-memb.</th><th>Non-memb. rev</th><th>Non-memb. AOV</th><th>Non-memb. freq</th></tr></thead>
  <tbody>{member_rows}</tbody></table></div>
</section>""")

SECTIONS.append(f"""
<section class="card">
  <h2>Revenue trend by business unit</h2>
  <p class="note">Invoiced revenue (ServiceTitan report 295) by brand, {months[0][2:] if months else '—'}/{months[0][:2] if months else ''} onwards. <strong>Data begins Oct 2024</strong> (ServiceTitan migration); revenue prior to that is not available in the system. FY24 shown as no-data, not zero.</p>
  <div class="chart-scroll">{svg_line_chart(trend_all, BRANDS, "Monthly invoiced revenue by brand", color_by=ACCENT) if trend_all else '<p>Monthly data still pulling</p>'}</div>
</section>""")

# KPI total by brand (from FY26 window in rev_by_bu)
fy26 = rev_by_bu.get("FY26", [])
tot_row = rep_rows_to_brand(fy26)
kpis = "".join(f'<div class="kpi"><div class="kn" style="color:{ACCENT.get(b,"#1D3B6D")}">{b}</div>'
               f'<div class="kv">{money(tot_row.get(b,0))}</div><div class="ku">FY26 invoiced</div></div>'
               for b in sorted(tot_row, key=tot_row.get, reverse=True))
SECTIONS.append(f'<section class="card"><h2>FY26 revenue by business unit</h2>{kpis}</section>')

# New vs repeat
rows = "".join(f'<tr><td>{brand_html(b)}</td><td>{c["distinct"]}</td><td>{c["new"]}</td><td>{c["repeat"]}</td>'
               f'<td>{c["repeat_pct"]:.1f}%</td></tr>'
               for b,c in sorted(cust_stats.items(), key=lambda x:-x[1]["distinct"]) if b!="Unassigned")
SECTIONS.append(f"""
<section class="card">
  <h2>New vs repeat customers</h2>
  <p class="note">Over the 5-year window (FY22–FY26). <em>New</em> = customer's first-ever job in the window; <em>repeat</em> = had a prior job in the window. Includes the Oct-2024 migration, so earlier history may under-count repeat customers.</p>
  <div class="tbl-wrap"><table><thead><tr><th>Business unit</th><th>Customers</th><th>New</th><th>Repeat</th><th>Repeat %</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>""")

# Bubble charts
for metric,label in [("rev","Total revenue per customer"),("aov","Average order value per customer")]:
    bubbles=""
    for b in BRANDS:
        cl = cust_rev.get(b, [])
        bubbles += f'<details><summary>Show {b} — {label}</summary><div class="chart-scroll">{svg_bubble(cl,b,metric)}</div></details>'
    SECTIONS.append(f'<section class="card"><h2>{label}</h2>{bubbles}</section>')

# ---------------------------------------------------------------------------
# Power of One — 1% calculator (interactive, grounded in real FY26 data)
# ---------------------------------------------------------------------------
base = load("powerofone_baseline.json", {})
P1_BASELINE_JSON = json.dumps(base) if base else "{}"
LEVERS = [
    ("price", "Price", "Rise paid on the same jobs; flows ~100% to gross profit (volume unchanged).", "profit", False),
    ("volume", "Volume", "More jobs at the same ticket; you keep the margin on the extra work.", "profit", False),
    ("cogs", "Cost of goods (direct costs)", "Cut material, equipment, PO and direct-labour costs on the cost base.", "profit", False),
    ("opex", "Operating expenses", "Cut overheads (wages, rent, IT, marketing, insurance). Basis = annual opex, enter below.", "profit", True),
    ("ar", "Accounts receivable", "Collect from debtors faster; frees cash, not reported profit.", "cash", False),
    ("inv", "Inventory / work-in-progress", "Reduce stock and WIP; frees cash, not reported profit.", "cash", True),
    ("ap", "Accounts payable", "Hold supplier payments a touch longer; retains cash, not reported profit.", "cash", True),
]
p1_rows = []
for key, name, desc, typ, needs_basis in LEVERS:
    basis = f'<input class="p1basisinp" type="number" step="1000" value="0" inputmode="numeric" aria-label="{esc.escape(name)} annual basis $">' if needs_basis else ""
    p1_rows.append(
        f'<div class="p1row" data-key="{key}" data-type="{typ}">'
        f'<div class="p1lab"><span class="p1name">{esc.escape(name)}</span>'
        f'<span class="p1desc">{esc.escape(desc)}</span></div>'
        f'<div class="p1ctl">'
        f'<input class="p1pct" type="number" step="0.1" value="1" inputmode="decimal" aria-label="{esc.escape(name)} % change">'
        f'<span class="p1pc">%</span></div>'
        f'<div class="p1ctl basis">{basis}</div>'
        f'<div class="p1out"><span class="p1sign"></span><span class="p1amt">—</span>'
        f'<span class="p1basis"></span></div></div>')
P1_SECTION = f"""
<section class="card" id="powerofone">
  <h2>Power of One — 1% calculator</h2>
  <p class="note">What a 1% improvement in each of the seven financial levers does to gross
  profit or cash, from live FY26 ServiceTitan data. Pick a business unit, dial each lever's %,
  and the effect updates instantly. <strong>Profit</strong> levers move gross profit;
  <strong>Cash</strong> levers move working capital, not reported profit. For Operating
  expenses, Inventory/WIP and Accounts payable (grey basis box), enter the annual $ basis first
  — those three are not yet fed from Xero/QB.</p>
  <label class="p1brandlbl">Business unit:
    <select id="p1brand"></select></label>
  <div class="p1grid" id="p1grid">{''.join(p1_rows)}</div>
  <div class="p1totals">
    <div class="p1total" id="p1profit"><span class="p1tl">Gross-profit effect (annual, pre-tax)</span><span class="p1tv">—</span></div>
    <div class="p1total" id="p1cash"><span class="p1tl">Cash / working-capital effect</span><span class="p1tv">—</span></div>
  </div>
  <p class="note" style="margin-top:12px">
    <strong>Basis:</strong> Price, Volume, COGS and Accounts receivable use live FY26 actuals from
    ServiceTitan (revenue report 295, gross margin from the job P&amp;L report, open invoice
    balances). The three grey-basis levers need the company P&amp;L and supplier ledger
    (Xero/QB) and return $0 until you type a basis. Default change is 1%; adjust any lever.
  </p>
</section>
"""
SECTIONS.insert(len(SECTIONS) - 1, P1_SECTION)  # before caveats

# ---------------------------------------------------------------------------
# Caveats
SECTIONS.append(f"""
<section class="card caveat">
  <h2>Method & caveats</h2>
  <ul>
    <li><strong>Revenue data availability:</strong> ServiceTitan financial data begins late Oct 2024. FY24 revenue is <em>not zero</em> — it is not recorded in the system. A true 3-year (FY24–26) trend requires FY24 actuals from Xero.</li>
    <li><strong>Cost to serve / gross profit:</strong> gross-margin figures in the Power of One calculator come from ServiceTitan's job P&amp;L report (452866873) over FY26 — real costed jobs, not an assumption. Operating-expense, inventory and payables bases are not yet fed from Xero/QB and must be typed in.</li>
    <li><strong>Invoice-based figures</strong> above are GST-inclusive totals and use the live window (Nov 2024+) where business-unit attribution is reliable.</li>
    <li><strong>Member vs non-member</strong> is based on ServiceTitan active Gold/Platinum memberships (1,316 active customers).</li>
    <li><strong>Migration blob:</strong> 3,559 jobs dated 1990-01-01 (created 2024-10-28, default business unit) are an import artefact and excluded from dated views.</li>
    <li><strong>Power of One method:</strong> the 1% calculator measures what a 1% change in each of seven financial levers does to gross profit or cash, from the Scaling Up 'Power of One' framework. <em>Price</em> rises flow ~100% to gross profit; <em>volume</em> only keeps the gross-margin % of the extra revenue; <em>COGS</em> and <em>operating expenses</em> save directly against their cost bases; <em>receivables</em>, <em>inventory/WIP</em> and <em>payables</em> move cash (working capital), not reported profit. Effects shown are annual, pre-tax, at the lever % you enter, and assume only that one lever moves (the others hold steady).</li>
    <li>Report generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ACST from ServiceTitan pulls.</li>
  </ul>
</section>""")

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>aba TRADES — Customer Lifetime Value Financial Report</title>
<style>
/*
 * aba TRADES CLV report — MOBILE-FIRST.
 * Base rules target small screens; min-width queries add structure.
 */
:root{{
--brand-primary:#1D3B6D;--brand-secondary:#2E528E;--brand-slate:#7789A7;--brand-dark-navy:#0B1D3B;
--brand-footer-navy:#172F57;--brand-surface:#EBEDF2;--brand-field:#F5F6F8;--brand-border:#D3D4DA;
--brand-bg:#FFFFFF;--brand-text:#1D3B6D;--font-body:'Futura PT','futura-pt',Helvetica,Arial,sans-serif;}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth}}
body{{font-family:var(--font-body);background:var(--brand-bg);color:var(--brand-text);line-height:1.55;
  overflow-x:hidden;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;height:auto}}

/* Header — compact by default, grows on wide screens */
.header{{background:var(--brand-primary);color:#fff;padding:26px 14px;text-align:center}}
.header .logo{{border-radius:50%;margin-bottom:8px;height:56px;width:56px}}
.header h1{{font-size:1.25rem;font-weight:700;line-height:1.25}}
.header p{{opacity:.85;margin-top:6px;font-size:.82rem;line-height:1.45}}

.container{{max-width:1180px;margin:0 auto;padding:12px 12px}}
.card{{background:#fff;border:1px solid var(--brand-border);border-radius:10px;padding:18px 14px;margin:14px 0}}
.card h2{{font-size:1.08rem;font-weight:700;color:var(--brand-primary);margin-bottom:8px}}
.note{{font-size:.84rem;color:#5a6577;margin-bottom:14px;line-height:1.5}}

/* KPI — stack full-width on phones */
.kpi-row{{display:flex;flex-direction:column;gap:10px;margin-bottom:14px}}
.kpi{{background:var(--brand-field);border:1px solid var(--brand-border);border-radius:10px;padding:14px 16px;width:100%}}
.kn{{font-weight:700;font-size:.85rem}} .kv{{font-size:1.3rem;font-weight:700;color:var(--brand-primary)}}
.ku{{font-size:.72rem;color:#5a6577}}

/* Tables — horizontal scroll on phones so columns never crush */
.tbl-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:8px;}}
.tbl-wrap table{{min-width:620px;margin:0}}
table{{width:100%;border-collapse:collapse;font-size:.88rem}}
th,td{{padding:10px 12px;border-bottom:1px solid var(--brand-border);text-align:right;white-space:nowrap}}
th{{background:var(--brand-surface);text-align:left;color:var(--brand-primary);font-weight:700}}
th:first-child,td:first-child{{text-align:left;white-space:normal;min-width:110px}}
tbody tr:nth-child(even){{background:var(--brand-field)}}

/* Charts — keep readable width, scroll sideways on phones */
.chart-scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;width:100%}}
.chart-scroll svg{{min-width:640px;max-width:none;height:auto;display:block}}
svg{{display:block;max-width:100%;height:auto}}

details{{margin:10px 0;background:var(--brand-field);border:1px solid var(--brand-border);border-radius:8px;padding:10px 12px}}
summary{{font-weight:700;color:var(--brand-primary);cursor:pointer}}
.caveat{{border-left:6px solid var(--brand-notice, #1E85BE)}} .caveat ul{{margin-left:18px}}
.caveat li{{margin-bottom:8px}}
.footer{{background:var(--brand-primary);color:#fff;padding:20px 14px;text-align:center;font-size:.78rem;line-height:1.45}}

/* Power of One calculator */
.p1brandlbl{{font-weight:700;color:var(--brand-primary);display:block;margin-bottom:10px}}
#p1brand{{font:inherit;padding:8px 10px;border:1px solid var(--brand-border);border-radius:8px;
  background:#fff;color:var(--brand-text);width:100%;max-width:400px}}
.p1grid{{display:grid;grid-template-columns:1fr;gap:10px}}
.p1row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:var(--brand-field);
  border:1px solid var(--brand-border);border-radius:9px;padding:12px}}
.p1lab{{flex:1 1 100%}}
.p1name{{display:block;font-weight:700;color:var(--brand-primary);font-size:.95rem}}
.p1desc{{display:block;font-size:.78rem;color:#5a6577;margin-top:2px}}
.p1ctl{{display:flex;align-items:center;gap:4px;flex:0 0 auto}}
.p1pct{{width:64px;font:inherit;font-weight:700;text-align:right;padding:6px 8px;
  border:1px solid var(--brand-border);border-radius:8px;background:#fff;color:var(--brand-text)}}
.p1pc{{color:#5a6577;font-weight:700}}
.p1basisinp{{width:132px;font:inherit;padding:6px 8px;border:1px dashed var(--brand-border);
  border-radius:8px;background:#eef0f4;color:var(--brand-text);text-align:right}}
.p1out{{flex:1 1 auto;min-width:128px;text-align:right}}
.p1sign{{font-weight:700}}
.p1amt{{font-weight:700;color:var(--brand-primary)}}
.p1basis{{display:block;font-size:.7rem;color:#5a6577}}
.p1row.good .p1sign{{color:#1f7a36}}
.p1row.bad .p1sign{{color:#b3392f}}
.p1totals{{display:flex;flex-direction:column;gap:10px;margin-top:14px}}
.p1total{{width:100%;background:var(--brand-primary);color:#fff;border-radius:9px;padding:14px 16px}}
.p1tl{{display:block;font-size:.8rem;opacity:.85}}
.p1tv{{display:block;font-size:1.5rem;font-weight:700}}

/* --- Scale up: tablets --- */
@media(min-width:600px){{
  .kpi-row{{flex-direction:row;flex-wrap:wrap}}
  .kpi{{flex:1 1 210px;width:auto;min-width:170px}}
  .p1total{{flex:1 1 auto;min-width:200px;width:auto}}
}}

/* --- Desktop --- */
@media(min-width:768px){{
  .header{{padding:44px 20px}}
  .header h1{{font-size:1.9rem}}
  .header p{{font-size:1rem}}
  .container{{padding:8px 16px}}
  .card{{padding:26px 22px;margin:22px 8px}}
  .card h2{{font-size:1.35rem}}
  .note{{font-size:.9rem}}
  .p1grid{{grid-template-columns:1fr 1fr}}
  .p1row{{flex-wrap:nowrap;justify-content:space-between}}
  .p1lab{{flex:1 1 auto}}
  .p1totals{{flex-direction:row}}
  .tbl-wrap{{overflow-x:visible}}
  .tbl-wrap table{{min-width:0}}
  .chart-scroll{{overflow-x:visible}}
  .chart-scroll svg{{min-width:0;max-width:100%}}
}}
</style></head><body>
<div class="header">
  <img src="{LOGO_URI}" alt="aba TRADES" class="logo">
  <h1>Customer Lifetime Value — Financial Report</h1>
  <p>aba TRADES · Revenue, customers &amp; order patterns · ServiceTitan data (Oct 2024 → present)</p></div>
<div class="container">{''.join(SECTIONS)}</div>
<div class="footer">aba Trades · Financial report for visual review · Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ACST</div>
<script>
(function(){{
var BASELINE = {P1_BASELINE_JSON} || {{}};
var order = ["Plumbing/Gas","Air Con","AEP","Electrical","Roofing","Renovations","Trades"];
function money(v){{ var s=v<0?"-$":"$"; v=Math.abs(v); return s+v.toLocaleString("en-US",{{minimumFractionDigits:0,maximumFractionDigits:0}}); }}
function compBase(key){{
  if(key==="_all"){{ var c=BASELINE._company||{{}}; return {{rev:c.revenue||0,gm:c.gm_pct||0,ar:c.ar||0,jobs:c.jobs||0}}; }}
  var b=BASELINE[key]||{{}}; return {{rev:b.revenue||0,gm:b.gm_pct||0,ar:b.ar||0,jobs:b.jobs||0}};
}}
var sel=document.getElementById("p1brand");
var o1=document.createElement("option");o1.value="_all";o1.textContent="All business units";sel.appendChild(o1);
order.forEach(function(b){{var o=document.createElement("option");o.value=b;o.textContent=b;sel.appendChild(o);}});
function compute(){{
  var key=sel.value; var B=compBase(key);
  var rev=B.rev, gm=B.gm, gms=gm/100, ar=B.ar;
  var profit={{price:0,volume:0,cogs:0,opex:0,itemized:{{}}}}, cash={{ar:0,inv:0,ap:0}};
  var totalsP=0, totalsC=0;
  document.querySelectorAll(".p1row").forEach(function(row){{
    var k=row.getAttribute("data-key"), typ=row.getAttribute("data-type");
    var pct=parseFloat(row.querySelector(".p1pct").value)||0;
    var basisInp=row.querySelector(".p1basisinp");
    var basisDollar=basisInp ? (parseFloat(basisInp.value)||0) : 0;
    var amt=0, basis="";
    if(k==="price"){{amt=rev*(pct/100); basis="on revenue "+money(rev);}}
    else if(k==="volume"){{amt=rev*(pct/100)*gms; basis=money(rev)+" rev x "+gm.toFixed(0)+"% GM";}}
    else if(k==="cogs"){{var cogs=rev*(1-gms); amt=cogs*(pct/100); basis="on COGS "+money(cogs);}}
    else if(k==="opex"){{amt=basisDollar*(pct/100); basis="annual opex "+money(basisDollar); if(!basisDollar)basis="enter annual opex basis";}}
    else if(k==="ar"){{amt=ar*(pct/100); basis="on open AR "+money(ar)+" (cash)";}}
    else if(k==="inv"){{amt=basisDollar*(pct/100); basis="annual inv/WIP "+money(basisDollar); if(!basisDollar)basis="enter inventory basis";}}
    else if(k==="ap"){{amt=basisDollar*(pct/100); basis="annual payables "+money(basisDollar); if(!basisDollar)basis="enter payables basis";}}
    row.querySelector(".p1sign").textContent=(amt>=0?"+":"-");
    row.querySelector(".p1amt").textContent=money(amt);
    row.querySelector(".p1basis").textContent=basis;
    row.querySelector(".p1basis").title=basis;
    row.classList.remove("good","bad"); row.classList.add(amt>=0?"good":"bad");
    if(typ==="profit")totalsP+=amt; else totalsC+=amt;
  }});
  document.getElementById("p1profit").querySelector(".p1tv").textContent=(totalsP>=0?"+":"-")+money(totalsP);
  document.getElementById("p1cash").querySelector(".p1tv").textContent=(totalsC>=0?"+":"-")+money(totalsC);
}}
sel.addEventListener("change",compute);
document.querySelectorAll(".p1pct, .p1basisinp").forEach(function(i){{i.addEventListener("input",compute);}});
compute();
}})();
</script>
</body></html>"""

out = os.path.join(D, "index.html")
open(out,"w").write(html)
print("WRITTEN", out, "bytes:", len(html))
print("months in trend:", len(months))