"""
Tyler EnerGov Citizen Self Service connector (sandbox).

Talks to the same public JSON API the portal's own search page uses. No login.
Shapes below were read off Gaston County's live portal (Oct 2026):

  GET  {base}/api/energov/search/criteria        blank search model
  POST {base}/api/energov/search/search          the search itself
  GET  {base}/api/energov/permits/permit/{id}    one permit: valuation, sqft,
                                                 contacts, custom fields

Every call needs the headers tenantId and Tyler-TenantUrl (Gaston: 1 / home).
The search only honours the date filters with SearchModule=2 and FilterModule=2
(permits), and PermitTypeId / PermitStatusId must be the string "none" rather
than null, or the server answers 500. That is what the portal's own JavaScript sends.
"""
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.request

UA = "brink-signals-sandbox/0.1 (+https://github.com/matchaking99/brink-signals)"

# Permit types that are never an industrial user (by the portal's type name).
RESIDENTIAL_TYPE = re.compile(
    r"residential|single.family|manufactured home|modular home|moved house|septic|well - well|"
    r"water heater|owner single trade|owner building|solar|family care", re.I)
# Commercial / industrial permit types, by the portal's type name.
COMMERCIAL_TYPE = re.compile(
    r"commercial|industrial|shell building|cell tower|temporary building|sprinkler|fire alarm|"
    r"^sign -|zoning - (change in use|commercial|site evaluation)", re.I)
# The building / site-work types inside that set. These get their details fetched first.
PRIMARY_TYPE = re.compile(
    r"building permit request: commercial|new building \(commercial\)|shell building|foundation only|"
    r"erosion (industrial|commercial)|zoning commercial\)|zoning - (commercial|change in use)|"
    r"demolition \(commercial\)", re.I)

# Contact roles, most useful first.
BUILDER_ROLES = ("contractor (gc)", "builder", "general contractor", "contractor")
OWNER_ROLES = ("owner", "property owner", "financial responsible party")


class EnerGov:
    def __init__(self, base, tenant_id="1", tenant_url="home", delay=1.0, retries=4):
        self.base = base.rstrip("/")
        self.headers = {"tenantId": str(tenant_id), "Tyler-TenantUrl": tenant_url,
                        "User-Agent": UA, "Accept": "application/json"}
        self.delay, self.retries = delay, retries
        self.calls = 0
        self._criteria = None

    def _req(self, path, body=None):
        url = self.base + path
        data = json.dumps(body).encode() if body is not None else None
        headers = dict(self.headers)
        if data is not None:
            headers["Content-Type"] = "application/json;charset=utf-8"
        last = None
        for attempt in range(self.retries):
            if self.calls:
                time.sleep(self.delay)        # be polite: one request at a time, spaced out
            self.calls += 1
            try:
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=90) as r:
                    out = json.load(r)
                if isinstance(out, dict) and out.get("Success") is False:
                    raise RuntimeError(f"EnerGov said no: {out.get('StatusCode')} {out.get('ErrorMessage')}")
                return out
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == self.retries - 1:
                    raise RuntimeError(f"HTTP {e.code} from {path}: {e.read()[:200]!r}") from e
                last = e
            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                last = e
            time.sleep(2 ** (attempt + 1))
        raise RuntimeError(f"{path} failed after {self.retries} tries: {last}")

    def criteria(self):
        if self._criteria is None:
            self._criteria = self._req("/api/energov/search/criteria")["Result"]
        return json.loads(json.dumps(self._criteria))   # fresh copy each time

    def search_permits(self, date_field, start, end, page_size=100, max_pages=60):
        """Yield permit search rows with {date_field}Date between start and end.
        date_field is "Issue" or "Apply"."""
        page = 1
        while page <= max_pages:
            c = self.criteria()
            c.update(SearchModule=2, FilterModule=2, PageNumber=page, PageSize=page_size,
                     SortBy="PermitNumber.keyword", SortAscending=False)
            c["PermitCriteria"].update({
                "PermitTypeId": "none", "PermitStatusId": "none",
                f"{date_field}DateFrom": f"{start.isoformat()}T00:00:00",
                f"{date_field}DateTo": f"{end.isoformat()}T23:59:59",
                "PageNumber": page, "PageSize": page_size,
                "SortBy": "PermitNumber.keyword", "SortAscending": False})
            res = self._req("/api/energov/search/search", c)["Result"]
            rows = res.get("EntityResults") or []
            yield from rows
            if not rows or page >= (res.get("TotalPages") or 0):
                return
            page += 1

    def permit(self, case_id):
        return self._req(f"/api/energov/permits/permit/{case_id}")["Result"]


def is_residential(row):
    return bool(RESIDENTIAL_TYPE.search(row.get("CaseType") or ""))


def is_commercial(row):
    t = row.get("CaseType") or ""
    return bool(COMMERCIAL_TYPE.search(t)) and not is_residential(row)


def is_primary(row):
    return bool(PRIMARY_TYPE.search(row.get("CaseType") or ""))


def custom_values(detail):
    """{FieldName: value} and {label: value} for filled custom fields, resolving
    pick lists. Field names differ by permit layout (BuildingArea2, ...), labels don't."""
    out = {}
    for cf in (detail or {}).get("CustomFields") or []:
        v = cf.get("Value")
        if v in (None, ""):
            continue
        picks = {p.get("CustomFieldPickListItemID"): p.get("Value") for p in cf.get("PickListItems") or []}
        v = picks.get(v, v)
        out.setdefault(cf.get("FieldName"), v)
        out.setdefault(" ".join((cf.get("Label") or "").split()).lower(), v)
    return out


def _contact_name(c):
    org = (c.get("GlobalEntityName") or "").strip()
    person = " ".join(x for x in ((c.get("FirstName") or "").strip(), (c.get("LastName") or "").strip()) if x)
    return org or person


def pick_contact(contacts, roles):
    for role in roles:
        for c in contacts:
            if (c.get("ContactTypeName") or "").strip().lower().startswith(role) and _contact_name(c):
                return _contact_name(c)
    return ""


def standardize(row, detail=None, portal="https://selfservice.gastongov.com/energov_prod/selfservice"):
    """One search row (+ optional detail) -> the bot's permit record shape, plus extras."""
    detail = detail or {}
    cf = custom_values(detail)
    contacts = detail.get("Contacts") or []
    sqft = detail.get("SquareFeet") or cf.get("total building area") or None
    value = detail.get("ValuationValue") or None
    occ = " / ".join(str(cf[k]) for k in ("OccupancyClassificationPrimary", "OccupancyClassificationSecondary")
                     if cf.get(k))
    desc_parts = [row.get("ProjectName") or cf.get("project name"), row.get("Description") or detail.get("Description")]
    site = " of ".join(f"{cf[k]} ac" for k in ("disturbed acreage", "total acreage") if cf.get(k))
    return {
        "permit_no": row.get("CaseNumber") or "",
        "issue_date": (row.get("IssueDate") or "")[:10],
        "apply_date": (row.get("ApplyDate") or "")[:10],
        "type": " - ".join(x for x in (row.get("CaseType"), row.get("CaseWorkclass")) if x),
        "occupancy": occ,
        "desc": " | ".join(dict.fromkeys(" ".join(str(p).split()) for p in desc_parts if p and str(p).strip())),
        "address": row.get("AddressDisplay") or "",
        "value": float(value) if value else None,
        "sqft": float(sqft) if sqft else None,
        "contractor": pick_contact(contacts, BUILDER_ROLES) or pick_contact(contacts, ("applicant",)),
        "owner": pick_contact(contacts, OWNER_ROLES),
        "status": row.get("CaseStatus") or "",
        "parcel": row.get("MainParcel") or "",
        "contacts": [(c.get("ContactTypeName") or "", _contact_name(c)) for c in contacts if _contact_name(c)],
        "work": cf.get("DWA1") or "",
        "site_acres": f"{site} disturbed" if " of " in site else site,
        "case_id": row.get("CaseId") or "",
        "url": f"{portal}#/permit/{row.get('CaseId')}",
    }


def pull(client, days=60, today=None, max_details=500, log=print):
    """Pull permits issued OR applied in the last `days`, fetch details for the
    commercial ones (building/site types first). Returns (rows, details, stats)."""
    today = today or dt.date.today()
    start = today - dt.timedelta(days=days)
    rows = {}
    for field in ("Issue", "Apply"):
        n = 0
        for r in client.search_permits(field, start, today):
            rows.setdefault(r["CaseId"], r)
            n += 1
        log(f"  {'issued' if field == 'Issue' else 'applied'} in window: {n}")
    commercial = [r for r in rows.values() if is_commercial(r)]
    commercial.sort(key=lambda r: (not is_primary(r), r.get("CaseNumber") or ""))
    details, problems = {}, []
    log(f"  commercial: {len(commercial)}; fetching up to {max_details} detail records")
    for i, r in enumerate(commercial[:max_details], 1):
        if i % 25 == 0:
            log(f"  details {i}/{min(len(commercial), max_details)}")
        try:
            details[r["CaseId"]] = client.permit(r["CaseId"])
        except RuntimeError as e:
            problems.append(f"detail {r.get('CaseNumber')}: {e}")
    if len(commercial) > max_details:
        problems.append(f"only fetched details for {max_details} of {len(commercial)} commercial permits")
    stats = {"pulled": len(rows), "commercial": len(commercial),
             "primary": sum(is_primary(r) for r in commercial), "details": len(details),
             "api_calls": client.calls}
    return rows, details, stats, problems
