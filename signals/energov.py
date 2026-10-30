"""
Live permits from Tyler EnerGov Citizen Self Service portals (Gaston County's
covers Gastonia and every town), matched to the county parcel layer for owner,
building and sale facts. Standard library only.

Contacts (applicant, contractor) are private on these portals ("you must be a
contact on this record"), so owner details come from the public parcel layer.
Proven in the sandbox branch (sandbox/permits) in Oct 2026.
"""
import copy
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from signals import permits

PAUSE = 1.0   # seconds between calls; these are county servers
BUDGET = 600  # seconds per portal; a slow county must not hold up the weekly run
_deadline = None

# Permit types worth a look (a source can override with "types_rx"). Trade-only
# and sign permits never mean a user moving.
COMMERCIAL = r"commercial|industrial|shell"
TRADES = re.compile(r"hvac|electrical|plumbing|mechanical|sign|roof|fire alarm|cell tower|sprinkler|"
                    r"flood|demolition|water heater|alcohol|refrigeration|gas pip", re.I)
# Industrial words the shared scorer doesn't carry.
EXTRA_INDUSTRIAL = ["plant", "machine shop", "fabricat", "assembly", "production"]
INDUSTRIAL_LAND = re.compile(r"industr|warehouse|manufactur|distribution|storage", re.I)
# Matches a keyword but isn't a user taking space (drone "docking stations", cell sites).
NOT_A_USER = re.compile(r"drone|antenna|verizon|at&t|t-mobile|cell (site|tower)|telecom|sports? (light|field)|"
                        r"pickleball|ballfield|restaurant|dental|church", re.I)
SQFT = re.compile(r"(\d{1,3}(?:,\d{3})+|\d{3,7})\s*(?:sf|s\.f\.|sq\.?\s*f(?:ee)?t)", re.I)


def _headers(src):
    return {"Content-Type": "application/json;charset=utf-8", "tenantId": str(src["tenant_id"]),
            "tenantName": src["tenant_name"], "Tyler-TenantUrl": "home",
            "User-Agent": "brink-signals/1.0 (weekly permit check)"}


def call(url, headers, body=None, tries=5):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        if _deadline and time.monotonic() > _deadline:
            raise TimeoutError(f"portal still answering slowly after {BUDGET}s; skipped this week")
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code < 500 or attempt == tries - 1:
                raise
            time.sleep(2 ** attempt * 2)


def recent_permits(src, days):
    """Every permit issued in the last `days`, newest first. The API ignores
    date filters, but sorting by issue date works, so page back to the cutoff."""
    h, api = _headers(src), src["api"]
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    template = call(api + "/search/criteria", h)["Result"]
    out = []
    for page in range(1, 200):
        c = copy.deepcopy(template)
        c.update(Keyword="", SearchModule=1, FilterModule=2, PageNumber=page, PageSize=100,
                 SortBy="IssueDate", SortAscending=False)
        c["PermitCriteria"].update(PageNumber=page, PageSize=100, SortBy="IssueDate", SortAscending=False)
        rows = (call(api + "/search/search", h, c)["Result"] or {}).get("EntityResults") or []
        out += [r for r in rows if (r.get("IssueDate") or "") >= cutoff]
        if not rows or (rows[-1].get("IssueDate") or "") < cutoff:
            return out
        time.sleep(PAUSE)
    return out


# Parcel-layer field names per county: key matches the permit's parcel number.
PARCEL_FIELDS = {
    "gaston": {"key": "PID", "owner": ["CURR_NAME1", "CURR_NAME2"], "mail": ["CURR_ADDR1", "CURR_CITY", "CURR_STATE"],
               "use": ["DESC1_DESC", "LAND_TYPE", "STRUCTTYPE"], "zoning": None, "sf": "SQFT", "built": "YEARBLT",
               "acres": "CALCAC", "area": "NBHDNAME", "sale_year": "SALE_YEAR", "sale_month": "SALE_MTH",
               "sale_amt": "SALESAMT"},
    "iredell": {"key": "PIN", "owner": ["Name"], "mail": ["ADD1", "CITY", "STATE"], "use": [], "zoning": "Zoning",
                "sf": "Actual_Heated_Area", "built": "AYB", "acres": "TaxAcres",
                "area": "TownshipLocationDescription", "sale_year": "Sale_Yr", "sale_month": None,
                "sale_amt": "Sales_Price"},
}


def parcel(src, pid):
    """The county parcel record for a permit's parcel number, or {}."""
    cfg = src.get("parcels")
    if not pid or not cfg:
        return {}
    key = PARCEL_FIELDS[cfg["fields"]]["key"]
    q = urllib.parse.urlencode({"where": f"{key}='{pid}'", "outFields": "*", "returnGeometry": "false", "f": "json"})
    feats = call(f"{cfg['url']}/query?{q}", {"User-Agent": "brink-signals/1.0"}).get("features") or []
    return feats[0]["attributes"] if feats else {}


def _join(*parts, sep=", "):
    return sep.join(str(x).strip() for x in parts if x and str(x).strip())


def facts(src, p):
    """Owner, land use / zoning and a one-line property note from a parcel record."""
    if not p:
        return {"owner": "", "use": "", "zoning": "", "note": ""}
    f = PARCEL_FIELDS[src["parcels"]["fields"]]
    g = lambda k: p.get(f[k]) if f.get(k) else None   # noqa: E731
    use = _join(*(p.get(k) for k in f["use"]))
    zoning = g("zoning") or ""
    sale = ""
    if g("sale_year"):
        sale = f"sold {g('sale_month') or '?'}/{g('sale_year')}" + (f" ${g('sale_amt'):,.0f}" if g("sale_amt") else "")
    mail = _join(*(p.get(k) for k in f["mail"]))
    note = _join((use.split(", ")[0] if use else ""), f"zoned {zoning}" if zoning else "",
                 f"{g('sf'):,.0f} SF" if g("sf") else "", f"built {g('built')}" if g("built") else "",
                 f"{g('acres')} ac" if g("acres") else "", g("area"), sale,
                 f"owner mail: {mail}" if mail else "", sep="; ")
    return {"owner": _join(*(p.get(k) for k in f["owner"]), sep=" & "), "use": use, "zoning": zoning, "note": note}


def pull(src, days):
    """Returns (permits issued, commercial records). Each record carries
    `industrial` and the permit table's usual fields plus `property`."""
    global _deadline
    _deadline = time.monotonic() + BUDGET
    h, api = _headers(src), src["api"]
    wanted = re.compile(src.get("types_rx", COMMERCIAL), re.I)
    rows = recent_permits(src, days)
    items = []
    for r in rows:
        if not wanted.search(r.get("CaseType") or "") or TRADES.search(r.get("CaseType") or ""):
            continue
        det = call(f"{api}/permits/{r['CaseId']}", h).get("Result") or {}
        time.sleep(PAUSE)
        p = facts(src, parcel(src, r.get("MainParcel") or det.get("MainParcelNumber")))
        desc = re.sub(r"\s+", " ", det.get("Description") or r.get("Description") or "").strip()
        m = SQFT.search(desc)
        rec = {"permit_no": r["CaseNumber"], "issue_date": (r.get("IssueDate") or "")[:10],
               "type": r.get("CaseType"), "desc": desc, "address": r.get("AddressDisplay") or "",
               "value": det.get("Value") or 0, "sqft": int(m.group(1).replace(",", "")) if m else 0,
               "status": det.get("PermitStatus") or r.get("CaseStatus"), "occupancy": None, "zoning": None,
               "contractor": None, "owner": p["owner"], "property": p["note"]}
        score, hits = permits.score(rec)
        text = desc.lower()
        hits += [w for w in EXTRA_INDUSTRIAL if permits.has(w, text)]
        if INDUSTRIAL_LAND.search(p["use"]) or any(permits.INDUSTRIAL_ZONING.match(z)
                                                   for z in re.split(r"[/,;\s]+", p["zoning"]) if z):
            hits.append("industrial property")
        rec["score"], rec["signals"] = max(score, 0) + 2 * ("industrial property" in hits), ", ".join(dict.fromkeys(hits))
        rec["industrial"] = score >= 0 and not NOT_A_USER.search(desc) and any(
            x in permits.INDUSTRIAL_HITS or x in EXTRA_INDUSTRIAL or x == "industrial property" for x in hits)
        items.append(rec)
    return len(rows), items
