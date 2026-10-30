"""
Live permits from Evolve Public portals: Union County NC and York County SC
(an older layout of the same software). Standard library only.

The portal is an ASP.NET page: open Permit Search, pick "Date Range" as the
search type (a postback that swaps in the date fields), search, then open
each commercial permit's public detail with its own postback from the results
page. Details carry the description, contractors, owner, parcel and zoning
(Union adds heated SF; York adds contract price and occupancy).
"""
import datetime as dt
import html
import http.cookiejar
import re
import time
import urllib.parse
import urllib.request

from signals import permits

PAUSE = 1.0   # seconds between calls; this is a county server
BUDGET = 600  # seconds per portal; a slow county must not hold up the weekly run
NOT_A_USER = re.compile(r"school|church|daycare|day care|group home|restaurant|kitchen cabinet|residen|"
                        r"cell (site|tower)|antenna|construction trailer|humane society", re.I)


class Portal:
    def __init__(self, src):
        self.url = src["url"]
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.op.addheaders = [("User-Agent", "brink-signals/1.0 (weekly permit check)"), ("Referer", self.url)]
        self.deadline = time.monotonic() + BUDGET

    def fetch(self, form=None, tries=4):
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        for attempt in range(tries):
            if time.monotonic() > self.deadline:
                raise TimeoutError(f"portal still answering slowly after {BUDGET}s; skipped this week")
            try:
                with self.op.open(self.url, data=data, timeout=60) as r:
                    return r.read().decode("utf-8", "replace")
            except (OSError, TimeoutError) as e:
                if getattr(e, "code", 500) < 500 or attempt == tries - 1:
                    raise
                time.sleep(2 ** attempt * 2)

    def post(self, page, target, argument="", **values):
        time.sleep(PAUSE)
        form = form_fields(page)
        form.update(values, __EVENTTARGET=target, __EVENTARGUMENT=argument)
        return self.fetch(form)


def form_fields(page):
    """The page's form values as a browser would post them back."""
    f = {}
    for m in re.finditer(r"<input[^>]+>", page):
        tag = m.group(0)
        name = re.search(r'name="([^"]+)"', tag)
        kind = re.search(r'type="([^"]+)"', tag)
        if not name or (kind and kind.group(1).lower() in ("checkbox", "radio", "submit", "button", "image")):
            continue
        val = re.search(r'value="([^"]*)"', tag)
        f[name.group(1)] = html.unescape(val.group(1)) if val else ""
    for m in re.finditer(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', page, re.S):
        opt = next((o for o in re.findall(r"<option[^>]*>", m.group(2)) if 'selected="selected"' in o), "")
        val = re.search(r'value="([^"]*)"', opt)
        f[m.group(1)] = html.unescape(val.group(1)) if val else ""
    return f


def _clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse_rows(page):
    """Results list -> [{address, permit_no, issued, type, contractor, target}]."""
    if "GV_SearchResults" in page:
        return parse_rows_grid(page)
    rows = {}
    for n, i, v in re.findall(r'id="ItemsList_LBT_ResultsLine(\d)_(\d+)"[^>]*>(.*?)</span>', page, re.S):
        rows.setdefault(int(i), {})[n] = _clean(v)
    for t, i in re.findall(r"__doPostBack\(&#39;(ItemsList\$ctl\d+\$LinkButton2)&#39;,&#39;&#39;\)\"[^>]*>"
                           r"<span id=\"ItemsList_LBT_ResultsLine1_(\d+)\"", page):
        rows.setdefault(int(i), {})["target"] = t
    out = []
    for r in rows.values():
        m = re.match(r"(\S+)\s*\((?:Issued|Completed|Finaled|\w+) (\d\d/\d\d/\d{4})\)", r.get("3", ""))
        out.append({"address": r.get("1", ""), "permit_no": m.group(1) if m else r.get("3", ""),
                    "issued": m.group(2) if m else "", "type": r.get("2", ""), "contractor": r.get("4", ""),
                    "target": r.get("target")})
    return out


def parse_rows_grid(page):
    """York's older layout: a one-letter category badge (C commercial, S land
    disturbance, R residential, M mechanical...), number (status), address."""
    rows = {}
    for key, i, v in re.findall(r'id="GV_SearchResults_LBT?_(Results\w+?)_(\d+)"[^>]*>(.*?)</(?:a|span)>', page, re.S):
        rows.setdefault(int(i), {})[key] = _clean(v)
    for i, t in re.findall(r'id="GV_SearchResults_LBT_ResultsDetails_(\d+)"[^>]*href="javascript:__doPostBack'
                           r"\(&#39;([^&]+)&#39;", page):
        rows.setdefault(int(i), {})["target"] = t
    out = []
    for r in rows.values():
        num = (r.get("ResultsLine1") or "").split(" (")[0]
        out.append({"address": r.get("ResultsLine2", ""), "permit_no": num, "issued": "",
                    "type": r.get("ResultsIndicator", ""), "contractor": r.get("ResultsLine3", ""),
                    "target": r.get("target")})
    return out


LABELS = ["Permit Num", "Permit Number", "Site Address", "Issued", "Report Code", "Description", "Heated SF",
          "Unheated SF", "Stories", "Permit Fields", "Contacts", "General", "Applicant", "Electrical", "Plumbing",
          "Mechanical", "Inspections", "Parcel ID", "Owner Name", "Owner Phone", "Zoning District", "Res Inspection",
          "Elect Inspection", "Jurisdiction", "GIS", "GIS Com Inspection", "Valuation", "Value", "Contract Price",
          "Status", "Expired Date", "Site Name", "NPDES No", "NPDES Approval Date", "TaxMapID", "Subdivision",
          "Lot Number", "Electric District", "Water District", "Council District", "Flood Zone", "Inspector",
          "MultiZoning", "Occupancy", "School District", "Type Name Organization"]


def _field(text, label):
    stops = "|".join(re.escape(x) for x in LABELS if x != label)
    m = re.search(rf"\b{re.escape(label)}\s+(.*?)\s+(?:{stops})\b", text)
    val = m.group(1).strip() if m else ""
    return "" if val in LABELS else val   # an empty field reads as the next label


def parse_detail(page):
    t = page[page.find("Permit Details"):] if "Permit Details" in page else page
    t = _clean(re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S))
    heated = _field(t, "Heated SF")
    price = _field(t, "Contract Price").replace("$", "").replace(",", "")
    issued = re.search(r"\bIssued (\d{1,2}/\d{1,2}/\d{4})", t)
    contacts = _field(t, "Type Name Organization")
    gc = re.search(r"\bContractor (.+?)(?= Contractor | Other |$)", contacts)
    return {"description": " | ".join(x for x in (_field(t, "Site Name"), _field(t, "Description")) if x),
            "report": _field(t, "Report Code"), "sqft": permits.to_num(heated) if heated else 0,
            "value": permits.to_num(price) if price else 0, "issued": issued.group(1) if issued else "",
            "general": _field(t, "General") or (gc.group(1) if gc else ""), "applicant": _field(t, "Applicant"),
            "owner": _field(t, "Owner Name"), "parcel": _field(t, "Parcel ID") or _field(t, "TaxMapID"),
            "zoning": _field(t, "Zoning District"), "occupancy": _field(t, "Occupancy"),
            "jurisdiction": _field(t, "Jurisdiction")}


def pull(src, days):
    """Returns (permits issued, commercial records). Each record carries
    `industrial` and the permit table's usual fields plus `property`."""
    p = Portal(src)
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    page = p.fetch()
    page = p.post(page, *src.get("search_menu", ("BL_Menu1", "1")))      # menu: Permit Search
    page = p.post(page, "DL_SearchType", DL_SearchType="Date Range")
    dates = {"DL_SearchType": "Date Range", "TB_SearchText1": start.strftime("%m/%d/%Y"),
             "TB_SearchText2": end.strftime("%m/%d/%Y")}
    if 'name="BT_Search"' in page:   # York: a plain submit button rather than a postback link
        results = p.post(page, "", BT_Search="Search", **dates)
    else:
        results = p.post(page, "BT_Search", **dates)
    rows = parse_rows(results)
    wanted = re.compile(src["types_rx"], re.I)
    items = []
    for r in rows:
        if not wanted.search(r["type"]) or not r["target"]:
            continue
        det = parse_detail(p.post(results, r["target"]))
        if src.get("skip_rx") and re.search(src["skip_rx"], det["report"], re.I):
            continue
        d = permits.to_date(r["issued"] or det["issued"])
        desc = det["description"]
        rec = {"permit_no": r["permit_no"], "issue_date": d.isoformat() if d else "",
               "type": det["report"] or r["type"], "desc": desc, "address": r["address"],
               "value": det["value"], "sqft": det["sqft"], "status": "Issued",
               "occupancy": det["occupancy"] or None, "zoning": det["zoning"] or None,
               "contractor": det["general"] or r["contractor"] or None, "owner": det["owner"],
               "property": "; ".join(x for x in (f"zoned {det['zoning']}" if det["zoning"] else "",
                                                 det["jurisdiction"],
                                                 f"parcel {det['parcel']}" if det["parcel"] else "") if x)}
        score, hits = permits.score(rec)
        rec["score"], rec["signals"] = max(score, 0), ", ".join(hits)
        rec["industrial"] = (score >= 0 and not NOT_A_USER.search(f"{desc} {det['owner']}")
                             and any(h in permits.INDUSTRIAL_HITS for h in hits))
        items.append(rec)
    return len(rows), items
