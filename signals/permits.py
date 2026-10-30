"""
Permit and planning-filing scoring, plus ArcGIS REST helpers.

Ported from the standalone pull_permits.py that was validated against
Mecklenburg's live permit layer (Oct 2026). Standard library only.
"""
import csv
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request

# Our column -> candidate field names (first match wins). Matching ignores case,
# spaces and punctuation, so "Issued Date", "ISSUED_DATE" and "issueddate" all
# match "issueddate". Set an exact name here if the guess is wrong.
FIELD_MAP = {
    "permit_no":  ["permitnum", "spermitnum", "b1altid", "zrno", "permitnumber", "permitno", "permit", "casenumber",
                   "caseno", "case", "projectnumber", "projectid", "devnumber"],
    "issue_date": ["issuedate", "dateissued", "issueddate", "issued", "approvaldate", "approveddate",
                   "dateapproved", "applieddate", "applicationdate", "submitteddate", "datesubmitted",
                   "dissued", "b1filedd", "meetingtime",
                   "date", "createddate"],
    "type":       ["permittype", "reviewtype", "worktype", "type", "casetype", "devtype", "developmenttype",
                   "projecttype"],
    "occupancy":  ["occupancy", "occupancycode", "usegroup", "occupancytype", "proposeduse", "usage", "landuse", "use"],
    "desc":       ["projectname", "projname", "description", "workdesc", "workdescription", "projdesc",
                   "permitdesc", "usdcdesc", "usdccodeanddescription", "descriptionofwork",
                   "typeofwork", "typeofbldg", "snameworkclass", "devname",
                   "developmentname", "name", "project", "notes", "comments", "request",
                   "requestcontinued"],
    "address":    ["projectaddress", "projadd", "address", "siteaddress", "fulladdress", "mainaddress",
                   "location", "streetaddress", "locationsite"],
    "value":      ["buildingcost", "bldgcost", "buildingconstructioncostcustomer",
                   "buildingconstructioncostsystem", "constcost", "valuation", "jobvalue", "projectvalue", "cost", "value"],
    "sqft":       ["squarefeet", "sqft", "ssqfeet", "totalsqft", "totalsquarefeet", "buildingsqft", "comsqft", "grossarea", "area"],
    "zoning":     ["zoningcode", "zonecode", "zoning", "zone", "zoningdistrict", "propsdzone",
                   "proposedzoning"],
    "contractor": ["contractor", "contractorname", "scompanynameparc", "gc", "applicant",
                   "applicantname", "developer",
                   "engineer"],
    "owner":      ["owner", "ownername", "ownname", "propertyowner"],
    "status":     ["permitstatus", "permitstat", "b1applstatus", "status", "casestatus", "devstatus", "approvalstatus"],
}

# Signal keywords. Score = sum of matched tier weights + value/zoning bonuses.
STRONG = ["rack", "mezzanine", "conveyor", "dock", "leveler", "esfr",
          "cold storage", "freezer", "cooler", "crane", "warehouse", "distribution",
          "manufactur", "industrial", "flex", "fulfillment", "logistics"]
MEDIUM = ["upfit", "up-fit", "tenant improvement", "addition", "expansion",
          "shell", "new building", "storage", "sprinkler", "high pile", "high-pile",
          "business park"]
# Work that matches a keyword but never means an operator expanding.
EXCLUDE = ["self storage", "self-storage", "mini storage", "mini-storage", "garage", "carport",
           "trash enclosure", "dumpster", "clarifier", "sludge", "pump station", "apartment",
           "retaining wall", "boat", "pier", "church", "school", "restaurant",
           "storage facility", "climate controlled", "tank farm", "automotive", "auto repair",
           "car wash", "trash room", "fuel", "re roof", "re-roof", "reroof", "roof replacement",
           "home sales", "relinquishment", "etj", "multifamily", "multi-family", "townhome",
           "(mf)", "apartments", "hospital", "medical center", "publix", "college", "university",
           "pre-wire", "prewire", "low voltage", "fire training"]
# Occupancy groups that are never industrial users: R = residential, U = utility/misc,
# A = assembly, E = educational, I = institutional.
NON_INDUSTRIAL_OCCUPANCY = re.compile(r"^\s*(R|U|A|E|I)-?\d?\s", re.I)
RESIDENTIAL = ["single family", "single-family", "residential", "dwelling", "townhome",
               "townhouse", "duplex", "deck", "pool", "subdivision"]
INDUSTRIAL_ZONING = re.compile(r"^(I-?\d|LI|HI|ML|MH|IND|BP|CBI|OFC-IND|M-?\d|I-?[GL]\b|PD-I\b)", re.I)
# Some counties split the address across columns (Rowan: number / direction /
# street / suffix).
ADDRESS_PARTS = ["saddress1", "spredirection", "saddress2", "sstreett"]
# Building-code occupancy groups: F = factory, S = storage/warehouse, H = high hazard.
# Mecklenburg writes these like "S1     * STORAGE - MODERATE HAZARD".
INDUSTRIAL_OCCUPANCY = re.compile(r"^\s*(F|S|H)-?\d", re.I)
# Category boilerplate that names every keyword regardless of the actual work,
# e.g. Mecklenburg's "437 - Commercial - Plan Review (Upfits, Additions, Repair)".
NOISE = re.compile(r"\(upfits, additions, repair\)", re.I)


def norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def fetch_json(url, params, post=False):
    headers = {"User-Agent": "brink-permit-pull/1.0"}
    body = urllib.parse.urlencode(params)
    if post:  # long objectIds lists would overflow a URL
        req = urllib.request.Request(url, data=body.encode(), headers=headers)
    else:
        req = urllib.request.Request(url + "?" + body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "error" in data:
        raise RuntimeError(f"ArcGIS error: {data['error']}")
    return data


def resolve_fields(field_names):
    names = {norm(n): n for n in field_names}
    fmap = {key: next((names[norm(c)] for c in cands if norm(c) in names), None)
            for key, cands in FIELD_MAP.items()}
    # Exports often split text across "Project Name" and "Description"; keep every
    # match so the keyword scoring sees all of it.
    fmap["desc"] = [names[norm(c)] for c in FIELD_MAP["desc"] if norm(c) in names] or None
    if not fmap["address"]:
        parts = [names[p] for p in ADDRESS_PARTS if p in names]
        fmap["address"] = parts or None
    return fmap


def to_date(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):  # ArcGIS epoch ms
        return dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc).date()
    s = str(v).strip()
    m = re.match(r"([A-Z][a-z]+ \d{1,2}, \d{4})", s)
    if m:
        try:
            return dt.datetime.strptime(m.group(1), "%B %d, %Y").date()
        except ValueError:
            pass
    for fmt, n in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d", 10), ("%m/%d/%Y", 10),
                   ("%m/%d/%y", 8), ("%Y%m%d", 8)):
        try:
            return dt.datetime.strptime(s.split(" ")[0] if n <= 10 else s[:n], fmt).date()
        except ValueError:
            pass
    return None


def to_num(v):
    try:
        return float(str(v).replace("$", "").replace(",", ""))
    except (TypeError, ValueError):
        return None


def fmt_num(v):
    return "" if v is None else int(v)


def has(word, text):
    # match at word start: "rack" hits "racking" but not mid-word
    lead = r"\b" if word[0].isalnum() else ""   # "(mf)" starts with punctuation
    return re.search(lead + re.escape(word), text) is not None


def score(rec):
    text = NOISE.sub("", " ".join(str(rec.get(k) or "") for k in ("type", "occupancy", "desc"))).lower()
    if any(has(w, text) for w in RESIDENTIAL) and not any(has(w, text) for w in STRONG):
        return -1, []
    if any(has(w, text) for w in EXCLUDE):
        return -1, []
    if rec.get("occupancy") and NON_INDUSTRIAL_OCCUPANCY.match(str(rec["occupancy"]) + " "):
        return -1, []
    hits, s = [], 0
    for w in STRONG:
        if has(w, text):
            hits.append(w); s += 2
    for w in MEDIUM:
        if has(w, text):
            hits.append(w); s += 1
    zones = re.split(r"[/,;\s]+", str(rec.get("zoning") or ""))
    if any(INDUSTRIAL_ZONING.match(z) for z in zones if z):
        hits.append("industrial zoning"); s += 2
    if rec.get("occupancy") and INDUSTRIAL_OCCUPANCY.match(str(rec["occupancy"])):
        hits.append("industrial occupancy"); s += 3
    sqft = rec.get("sqft") or 0
    if sqft >= 50_000:
        s += 3; hits.append("50k+ SF")
    elif sqft >= 10_000:
        s += 2; hits.append("10k+ SF")
    val = rec.get("value") or 0
    if val >= 1_000_000:
        s += 3; hits.append("$1M+")
    elif val >= 250_000:
        s += 2; hits.append("$250k+")
    elif val >= 100_000:
        s += 1; hits.append("$100k+")
    return s, hits


def build_rec(attrs, fmap, cutoff):
    """Map one source row to our columns. Returns None if it's older than cutoff."""
    rec = {k: (attrs.get(v) if v else None) for k, v in fmap.items() if k not in ("desc", "address")}
    addr = fmap["address"]
    if isinstance(addr, list):
        rec["address"] = " ".join(str(attrs.get(c) or "").strip() for c in addr if attrs.get(c))
    else:
        rec["address"] = attrs.get(addr) if addr else None
    parts = [str(attrs.get(c) or "").strip() for c in (fmap["desc"] or [])]
    rec["desc"] = " | ".join(dict.fromkeys(p for p in parts if p))
    d = to_date(rec["issue_date"])
    if cutoff and d and d < cutoff:
        return None
    rec["issue_date"] = d.isoformat() if d else ""
    if isinstance(rec.get("permit_no"), float) and rec["permit_no"].is_integer():
        rec["permit_no"] = str(int(rec["permit_no"]))
    rec["value"] = to_num(rec["value"])
    rec["sqft"] = to_num(rec["sqft"])
    return rec


def date_wheres(date_f, date_type, cutoff):
    """WHERE clauses for 'issued on/after cutoff', most to least standard.
    Servers differ on date-literal syntax, so callers try each in turn."""
    if date_type == "esriFieldTypeDate":
        return [f"{date_f} >= DATE '{cutoff}'",
                f"{date_f} >= timestamp '{cutoff} 00:00:00'",
                f"{date_f} >= '{cutoff}'"]
    return []  # text dates can't be range-filtered reliably; caller falls back


def query(layer_url, params, post=False):
    """Run a search against a layer. Searches go to <layer>/query; the bare
    layer URL only describes the layer."""
    return fetch_json(layer_url + "/query", params, post)


def query_ids(url, where):
    data = query(url, {"where": where, "returnIdsOnly": "true", "f": "json"})
    return data.get("objectIdFieldName"), data.get("objectIds") or []


def pick_where(url, meta, fmap, cutoff):
    """WHERE clause for 'issued since cutoff' that this server accepts.
    Returns "1=1" for layers without a date field, None if every date filter
    is rejected (the caller then falls back to the newest records by ID)."""
    date_f = fmap["issue_date"]
    if not date_f:
        return "1=1"
    ftype = next((f.get("type") for f in meta["fields"] if f["name"] == date_f), None)
    for where in date_wheres(date_f, ftype, cutoff):
        try:
            query(url, {"where": where, "returnCountOnly": "true", "f": "json"})
            return where
        except Exception:
            continue
    return None


def fetch_by_ids(url, ids, batch):
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        data = query(url, {"objectIds": ",".join(map(str, chunk)), "outFields": "*",
                           "returnGeometry": "false", "f": "json"}, post=True)
        yield from (feat["attributes"] for feat in data.get("features", []))


def rows_from_arcgis(url, fmap, meta, cutoff, recent_cap=20000):
    """Download matching records with pyesridump (github.com/openaddresses/pyesridump),
    which handles paging, ID-range and retry quirks across ArcGIS servers."""
    from esridump.dumper import EsriDumper

    where = pick_where(url, meta, fmap, cutoff)
    if where is not None:
        print(f"  where: {where}", file=sys.stderr)
        dump = EsriDumper(url, extra_query_args={"where": where}, request_geometry=False,
                          timeout=60, pause_seconds=1, requests_to_pause=20)
        attrs = (feat.get("properties") or {} for feat in dump)  # GeoJSON features
    else:
        # No date filter accepted: newest records by object ID, dated client-side.
        print(f"  no date filter accepted; scanning newest {recent_cap} by ID", file=sys.stderr)
        _, ids = query_ids(url, "1=1")
        attrs = fetch_by_ids(url, sorted(ids)[-recent_cap:], 1000)
    use_cutoff = cutoff if fmap["issue_date"] else None
    for a in attrs:
        rec = build_rec(a, fmap, use_cutoff)
        if rec is not None:
            yield rec


def rows_from_file(path, fmap, cutoff):
    for row in read_csv(path):
        rec = build_rec(row, fmap, cutoff)
        if rec is not None:
            yield rec


def read_csv(path):
    # Excel "CSV UTF-8" adds a BOM; utf-8-sig strips it.
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def describe_service(layer_url):
    """When a layer URL fails, list what the parent service actually offers."""
    root = re.sub(r"/\d+/?$", "", layer_url)
    try:
        meta = fetch_json(root, {"f": "json"})
    except Exception as e:
        return f"The service itself didn't answer either ({e}). Paste this output to Claude."
    layers = meta.get("layers", []) + meta.get("tables", [])
    if not layers:
        return f"{root} answered but lists no layers. Paste this output to Claude."
    lines = [f"Layers available at {root}:"]
    lines += [f"  --url {root}/{l['id']}    ({l['name']})" for l in layers]
    return "\n".join(lines) + "\nRe-run --inspect with the --url of the right layer."


def pull_arcgis(url, days, fields=None):
    """Yield mapped records issued within `days` from an ArcGIS layer.
    `fields` overrides the guessed mapping, e.g. {"zoning": "ReqZone"}."""
    meta = fetch_json(url, {"f": "json"})
    if not meta.get("fields"):
        raise RuntimeError(f"{url} returned no fields; is it a layer URL?")
    fmap = resolve_fields([f["name"] for f in meta["fields"]])
    fmap.update(fields or {})
    cutoff = dt.date.today() - dt.timedelta(days=days)
    return list(rows_from_arcgis(url, fmap, meta, cutoff)), fmap


def discover_layer(service_url, name_pattern):
    """Find the newest layer on a service whose name matches `name_pattern`
    (e.g. Cabarrus publishes one "Permits <year>" layer per year)."""
    meta = fetch_json(service_url, {"f": "json"})
    rx = re.compile(name_pattern, re.I)
    hits = [l for l in meta.get("layers", []) if rx.search(l.get("name", ""))]
    if not hits:
        return None
    # Prefer the highest 4-digit year in the name, else the highest layer id.
    def key(l):
        years = [int(y) for y in re.findall(r"(?:19|20)\d\d", l["name"])]
        return (max(years) if years else 0, l["id"])
    best = max(hits, key=key)
    return f"{service_url.rstrip('/')}/{best['id']}", best["name"], key(best)[0]


INDUSTRIAL_HITS = set(STRONG) | {"industrial zoning", "industrial occupancy"}


def is_industrial(rec):
    return any(h.strip() in INDUSTRIAL_HITS for h in (rec.get("signals") or "").split(","))


def score_records(records, min_score):
    out = []
    for rec in records:
        s, hits = score(rec)
        if s >= min_score:
            rec["score"], rec["signals"] = s, ", ".join(dict.fromkeys(hits))
            out.append(rec)
    out.sort(key=lambda r: (r["score"], r["value"] or 0), reverse=True)
    return out


def score_csv(path, days, min_score):
    """Score a permit export someone dropped in inbox/ (Gaston CSS, Union
    Evolve, Iredell eTRAKiT, ...)."""
    rows = read_csv(path)
    if not rows:
        return []
    fmap = resolve_fields(list(rows[0].keys()))
    cutoff = dt.date.today() - dt.timedelta(days=days)
    return score_records(rows_from_file(path, fmap, cutoff), min_score)


# ---- inspection results (Union County publishes these, not permits) --------

# Inspection names that only happen on commercial jobs. Union labels them
# "Comm Building Final", "Fire Final", "Comm Electrical Rough In", ...
COMMERCIAL_INSPECTION = re.compile(r"^\s*(comm|fire)\b|commercial|sprinkler|fire alarm|hood", re.I)
# The inspections that mean the building is ready to occupy.
FINAL = re.compile(r"(building|fire)\b.*\bfinal|final\b.*\b(building|fire)|certificate of occupancy", re.I)


def pull_inspections(url, days, date_field="inspection_date"):
    """Commercial jobs with an inspection in the last `days`, one row per
    permit: address, stage (under construction / final) and what was inspected."""
    from esridump.dumper import EsriDumper

    meta = fetch_json(url, {"f": "json"})
    cutoff = dt.date.today() - dt.timedelta(days=days)
    where = pick_where(url, meta, {"issue_date": date_field}, cutoff)
    if where is None:
        raise RuntimeError(f"{url}: no date filter accepted on {date_field}")
    dump = EsriDumper(url, extra_query_args={"where": where}, request_geometry=False,
                      timeout=60, pause_seconds=1, requests_to_pause=20)
    jobs = {}
    for feat in dump:
        a = feat.get("properties") or {}
        name = (a.get("inspection_name") or "").strip()
        if not COMMERCIAL_INSPECTION.search(name):
            continue
        d = to_date(a.get(date_field))
        if d is None or d < cutoff:
            continue
        pid = str(a.get("permit_id") or a.get("acctno") or a.get("address"))
        j = jobs.setdefault(pid, {"permit_no": pid, "address": re.sub(r"\s+", " ", a.get("address") or "").strip(),
                                  "parcel": a.get("parcel"), "inspections": set(), "latest": d,
                                  "statuses": set()})
        j["inspections"].add(name)
        j["statuses"].add(a.get("inspection_status") or "")
        j["latest"] = max(j["latest"], d)
    out = []
    for j in jobs.values():
        j["stage"] = "final" if any(FINAL.search(n) for n in j["inspections"]) else "under construction"
        j["inspections"] = sorted(j["inspections"])
        j["latest"] = j["latest"].isoformat()
        out.append(j)
    out.sort(key=lambda j: (j["stage"] == "final", j["latest"]), reverse=True)
    return out
