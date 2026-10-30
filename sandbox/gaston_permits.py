"""
SANDBOX: live Gaston County permits from the county's public EnerGov Citizen
Self Service API, matched to the county parcel layer for owner, building and
sale facts. Not wired into run_weekly.py; see sandbox/README.md.

  python3 sandbox/gaston_permits.py [days]      # writes sandbox/output/

Contacts (applicant, contractor) are private on this portal ("you must be a
contact on this record"), so owner details come from the public parcel layer.
"""
import copy
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from signals import permits  # noqa: E402

API = "https://selfservice.gastongov.com/energov_prod/selfservice/api/energov"
PARCELS = "https://gis.gastoncountync.gov/publicgis/rest/services/PublicGIS/Parcels/FeatureServer/11"
HEADERS = {"Content-Type": "application/json;charset=utf-8", "tenantId": "1",
           "tenantName": "Gaston County, NC", "Tyler-TenantUrl": "home",
           "User-Agent": "brink-signals/0.1 (weekly permit check)"}
PAUSE = 1.0   # seconds between calls; this is a county server

# Permit types worth a look. Trade-only and sign permits never mean a user moving.
COMMERCIAL = re.compile(r"commercial|industrial|shell", re.I)
TRADES = re.compile(r"hvac|electrical|plumbing|mechanical|sign|roof|fire alarm|cell tower|sprinkler|"
                    r"flood|demolition|water heater|alcohol", re.I)
# Industrial words the shared scorer doesn't carry.
EXTRA_INDUSTRIAL = ["plant", "machine shop", "fabricat", "assembly", "production"]
INDUSTRIAL_LAND = re.compile(r"industr|warehouse|manufactur|distribution|storage", re.I)
# Matches a keyword but isn't a user taking space (drone "docking stations", cell sites).
NOT_A_USER = re.compile(r"drone|antenna|verizon|at&t|t-mobile|cell (site|tower)|telecom", re.I)
SQFT = re.compile(r"(\d{1,3}(?:,\d{3})+|\d{3,7})\s*(?:sf|s\.f\.|sq\.?\s*f(?:ee)?t)", re.I)


def call(path, body=None, base=None, tries=5):
    url = (base or API) + path
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code < 500 or attempt == tries - 1:
                raise
            time.sleep(2 ** attempt * 2)


def recent_permits(days):
    """Every permit issued in the last `days`, newest first. The API ignores
    date filters, but sorting by issue date works, so page back to the cutoff."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    template = call("/search/criteria")["Result"]
    out = []
    for page in range(1, 200):
        c = copy.deepcopy(template)
        c.update(Keyword="", SearchModule=1, FilterModule=2, PageNumber=page, PageSize=100,
                 SortBy="IssueDate", SortAscending=False)
        c["PermitCriteria"].update(PageNumber=page, PageSize=100, SortBy="IssueDate", SortAscending=False)
        rows = (call("/search/search", c)["Result"] or {}).get("EntityResults") or []
        out += [r for r in rows if (r.get("IssueDate") or "") >= cutoff]
        if not rows or (rows[-1].get("IssueDate") or "") < cutoff:
            return out
        time.sleep(PAUSE)
    return out


def parcel(pid):
    if not pid:
        return {}
    q = urllib.parse.urlencode({"where": f"PID='{pid}'", "outFields": "*", "returnGeometry": "false", "f": "json"})
    feats = call(f"/query?{q}", base=PARCELS).get("features") or []
    return feats[0]["attributes"] if feats else {}


def _sale(p):
    if p.get("SALE_YEAR"):
        amt = f" for ${p['SALESAMT']:,.0f}" if p.get("SALESAMT") else ""
        return f"{p.get('SALE_MTH') or '?'}/{p['SALE_YEAR']}{amt}"
    return ""


def build(rows):
    """Commercial permits -> enriched records, industrial ones flagged."""
    items = []
    for r in rows:
        if not COMMERCIAL.search(r.get("CaseType") or "") or TRADES.search(r.get("CaseType") or ""):
            continue
        det = call(f"/permits/{r['CaseId']}").get("Result") or {}
        time.sleep(PAUSE)
        p = parcel(r.get("MainParcel") or det.get("MainParcelNumber"))
        desc = re.sub(r"\s+", " ", det.get("Description") or r.get("Description") or "").strip()
        m = SQFT.search(desc)
        rec = {"permit_no": r["CaseNumber"], "issue_date": (r.get("IssueDate") or "")[:10],
               "type": r.get("CaseType"), "desc": desc, "address": r.get("AddressDisplay") or "",
               "value": det.get("Value") or 0, "sqft": int(m.group(1).replace(",", "")) if m else 0,
               "status": det.get("PermitStatus") or r.get("CaseStatus"), "occupancy": None, "zoning": None,
               "parcel": r.get("MainParcel"),
               "owner": " & ".join(x.strip() for x in (p.get("CURR_NAME1"), p.get("CURR_NAME2")) if x and x.strip()),
               "owner_mail": ", ".join(x.strip() for x in (p.get("CURR_ADDR1"), p.get("CURR_CITY"), p.get("CURR_STATE"))
                                       if x and x.strip()),
               "land_use": p.get("DESC1_DESC") or p.get("LAND_TYPE") or "",
               "building_sf": p.get("SQFT") or 0, "year_built": p.get("YEARBLT") or "",
               "acres": p.get("CALCAC") or "", "last_sale": _sale(p), "area": p.get("NBHDNAME") or "",
               "assessed": p.get("TOTVAL") or 0}
        score, hits = permits.score(rec)
        text = desc.lower()
        hits += [w for w in EXTRA_INDUSTRIAL if permits.has(w, text)]
        if INDUSTRIAL_LAND.search(f"{rec['land_use']} {p.get('LAND_TYPE') or ''} {p.get('STRUCTTYPE') or ''}"):
            hits.append("industrial property")
        rec["score"], rec["signals"] = score, ", ".join(dict.fromkeys(hits))
        rec["industrial"] = score >= 0 and not NOT_A_USER.search(desc) and any(h in permits.INDUSTRIAL_HITS or h in EXTRA_INDUSTRIAL
                                               or h == "industrial property" for h in hits)
        items.append(rec)
    return items


def report(items, pulled, days):
    ind = [i for i in items if i["industrial"]]
    L = [f"# SANDBOX — Gaston live permits, last {days} days ({dt.date.today()})", "",
         f"{pulled} permits issued · {len(items)} commercial · **{len(ind)} industrial**", ""]
    seen = set()
    for i in sorted(ind, key=lambda x: x["issue_date"], reverse=True):
        if i["address"] not in seen:   # several permits at one site read as one project
            seen.add(i["address"])
            L.append(f"## {i['address']}")
        L += [f"- **Permit {i['permit_no']}** ({i['type']}), issued {i['issue_date']}, "
              f"value ${i['value']:,.0f}" + (f", {i['sqft']:,} SF in scope" if i["sqft"] else ""),
              f"  - **Work:** {i['desc'] or '(no description)'}",
              f"- **Owner:** {i['owner'] or 'unknown'}" + (f" (mail: {i['owner_mail']})" if i["owner_mail"] else ""),
              f"- **Property:** {i['land_use'] or '?'}"
              + (f", {i['building_sf']:,.0f} SF" if i["building_sf"] else "")
              + (f", built {i['year_built']}" if i["year_built"] else "")
              + (f", {i['acres']} ac" if i["acres"] else "") + (f", {i['area']}" if i["area"] else "")
              + (f"; last sale {i['last_sale']}" if i["last_sale"] else ""),
              f"- _Signals: {i['signals']}_", ""]
    other = [i for i in items if not i["industrial"]]
    if other:
        L += ["## Other commercial permits (not industrial)", ""]
        L += [f"- {i['issue_date']} {i['permit_no']} · {i['address']} · {i['desc'][:90]}" for i in other]
    return "\n".join(L) + "\n"


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rows = recent_permits(days)
    items = build(rows)
    out = ROOT / "sandbox" / "output"
    out.mkdir(parents=True, exist_ok=True)
    (out / "items.json").write_text(json.dumps(items, indent=1))
    (out / "report.md").write_text(report(items, len(rows), days))
    print(f"{len(rows)} permits, {len(items)} commercial, {sum(i['industrial'] for i in items)} industrial")


if __name__ == "__main__":
    main()
