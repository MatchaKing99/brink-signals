"""
Live permits from Accela Citizen Access portals (Cabarrus County's covers the
county, Harrisburg, Kannapolis, Midland and Mount Pleasant). Standard library
only.

The portal is an ASP.NET form: GET the search page, post the permit type and
date range back with the page's hidden fields, then follow "Next >" postbacks.
Each record's public detail page carries the applicant, contractor, owner,
description, occupancy, estimated cost and square feet.
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
FORM = "ctl00$PlaceHolderMain$generalSearchForm$"
SEARCH_BUTTON = "ctl00$PlaceHolderMain$btnNewSearch"
NOT_A_USER = re.compile(r"school|church|playground|shelter|guardhouse|ev charger|sports field|hospital|nicu|"
                        r"daycare|restaurant|deli\b|pizzeria|retail suite|dealership|showroom|salon|"
                        r"apartment|cell (site|tower)|antenna", re.I)


def _name(s):
    """'ACME LLC 123 MAIN ST ...' -> 'ACME LLC'; owners read 'NAME * address'."""
    s = (s or "").split(" * ")[0]
    return re.split(r"\s(?=\d)|\s(?:PO|P O) BOX", s, maxsplit=1)[0].strip(" ,")


class Portal:
    def __init__(self, src):
        self.src = src
        self.base = src["base"].rstrip("/")
        self.search_url = f"{self.base}/Cap/CapHome.aspx?module={src.get('module', 'Permits')}&TabName=Permits"
        origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(self.base))
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        # The portal rejects form posts without Referer/Origin (CSRF check), as a browser would send.
        self.op.addheaders = [("User-Agent", "brink-signals/1.0 (weekly permit check)"),
                              ("Referer", self.search_url), ("Origin", origin)]
        self.deadline = time.monotonic() + BUDGET

    def fetch(self, url, form=None, tries=4):
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        for attempt in range(tries):
            if time.monotonic() > self.deadline:
                raise TimeoutError(f"portal still answering slowly after {BUDGET}s; skipped this week")
            try:
                with self.op.open(url, data=data, timeout=30) as r:
                    return r.read().decode("utf-8", "replace")
            except (OSError, TimeoutError) as e:
                if getattr(e, "code", 500) < 500 or attempt == tries - 1:
                    raise
                time.sleep(2 ** attempt * 2)

    def search(self, permit_type, start, end):
        """Every record of one type opened between start and end (dates)."""
        page = self.fetch(self.search_url)
        form = form_fields(page)
        form.update({FORM + "ddlGSPermitType": permit_type,
                     FORM + "txtGSStartDate": start.strftime("%m/%d/%Y"),
                     FORM + "txtGSEndDate": end.strftime("%m/%d/%Y"),
                     "__EVENTTARGET": SEARCH_BUTTON, "__EVENTARGUMENT": ""})
        rows = []
        for _ in range(30):
            time.sleep(PAUSE)
            page = self.fetch(self.search_url, form)
            rows += parse_rows(page, self.base)
            nxt = re.search(r"__doPostBack\(&#39;([^&]+)&#39;,&#39;&#39;\)\"[^>]*>Next", page)
            if not nxt:
                break
            form = form_fields(page)
            form.update({"__EVENTTARGET": nxt.group(1), "__EVENTARGUMENT": ""})
        return rows


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


def _span(row, key):
    m = re.search(rf'id="[^"]*_{key}[^"]*"[^>]*>(.*?)</span>', row, re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""


def parse_rows(page, base):
    out = []
    for row in re.findall(r'<tr[^>]*class="ACA_TabRow_(?:Odd|Even)[^"]*"[^>]*>.*?</tr>', page, re.S):
        link = re.search(r'href="(/[^"]*CapDetail\.aspx[^"]*)"', row)
        num = _span(row, "lblPermitNumber")
        if not num:
            continue
        out.append({"date": _span(row, "lblUpdatedTime"), "permit_no": num, "type": _span(row, "lblType"),
                    "project": _span(row, "lblProjectName"), "address": _span(row, "lblAddress"),
                    "status": _span(row, "lblStatus"), "note": _span(row, "lblShortNote"),
                    "url": urllib.parse.urljoin(base, html.unescape(link.group(1))) if link else ""})
    return out


def _text(page):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def _after(text, label, stops):
    m = re.search(re.escape(label) + r"\s*(.*?)\s*(?:" + "|".join(map(re.escape, stops)) + r")", text)
    return m.group(1).strip(" *") if m else ""


DETAIL_STOPS = ["Licensed Professional:", "Project Description:", "Owner:", "More Details", "Additional Information",
                "Application Information", "Parcel Information", "Number of Buildings:", "Construction Type:",
                "Occupancy:", "Estimated Cost:", "Jurisdiction:", "Estimated Sqft:", "No Charge:", "Subdivision:",
                "Home Phone:", "Work Phone:", "Mobile Phone:"]


def parse_detail(page):
    t = _text(page)
    stops = DETAIL_STOPS
    cost = _after(t, "Estimated Cost:", stops)
    sqft = _after(t, "Estimated Sqft:", stops)
    applicant = _after(t, "Applicant:", stops)
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", applicant)
    return {"applicant": re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", applicant).strip(),
            "applicant_email": email.group(0) if email else "",
            "contractor": _after(t, "Licensed Professional:", stops),
            "contractor_phone": _after(t, "Home Phone:", ["BUILDING", "Project Description:", "Work Phone:"])
            or _after(t, "Work Phone:", ["BUILDING", "Project Description:"]),
            "description": _after(t, "Project Description:", stops),
            "owner": _after(t, "Owner:", stops), "construction": _after(t, "Construction Type:", stops),
            "occupancy": _after(t, "Occupancy:", stops), "jurisdiction": _after(t, "Jurisdiction:", stops),
            "value": permits.to_num(cost.replace(",", "")) if cost else 0,
            "sqft": permits.to_num(sqft.replace(",", "")) if sqft else 0,
            "parcel": (re.search(r"Parcel Number:\s*(\d+)", t) or [None, ""])[1]}


def pull(src, days):
    """Returns (records found, commercial records). Each record carries
    `industrial` and the permit table's usual fields plus `property`."""
    p = Portal(src)
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    rows = {}
    for t in src["types"]:
        for r in p.search(t, start, end):
            rows.setdefault(r["permit_no"], r)
    items = []
    for r in rows.values():
        det = {}
        if r["url"]:
            time.sleep(PAUSE)
            det = parse_detail(p.fetch(r["url"]))
        d = permits.to_date(r["date"])
        desc = " | ".join(dict.fromkeys(x for x in (det.get("description") or r["project"], r["note"],
                                                    det.get("construction")) if x))
        contact = ", ".join(x for x in (det.get("applicant"), det.get("applicant_email"),
                                        det.get("contractor_phone") and f"ph {det['contractor_phone']}") if x)
        rec = {"permit_no": r["permit_no"], "issue_date": d.isoformat() if d else "", "type": r["type"],
               "desc": desc, "address": r["address"], "value": det.get("value") or 0, "sqft": det.get("sqft") or 0,
               "status": r["status"], "occupancy": det.get("occupancy") or None, "zoning": None,
               "contractor": _name(det.get("contractor")) or None, "owner": _name(det.get("owner")),
               "property": "; ".join(x for x in (det.get("occupancy"), det.get("jurisdiction"),
                                                 "owner mail: " + det["owner"].split(" * ", 1)[1]
                                                 if " * " in det.get("owner", "") else "",
                                                 f"parcel {det['parcel']}" if det.get("parcel") else "",
                                                 f"applicant: {contact}" if contact else "") if x)}
        score, hits = permits.score(rec)
        rec["score"], rec["signals"] = max(score, 0), ", ".join(hits)
        rec["industrial"] = (score >= 0 and not NOT_A_USER.search(desc)
                             and any(h in permits.INDUSTRIAL_HITS for h in hits))
        items.append(rec)
    return len(rows), items
